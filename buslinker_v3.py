"""BusLinker V3.0: driver, graficos, IDs e calibracao LX-225.

Arquivo autonomo; dependencias externas: pyserial e matplotlib.
Gerado por tools/build_standalone.py; edite os modulos fonte para regenerar.
"""

from __future__ import annotations

import math
import struct
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import serial


# Parâmetros do barramento e limites usados pelo LX-225.
BAUDRATE = 115200
READ_TIMEOUT_S = 0.045
ANGLE_MIN_DEG = 0.0
ANGLE_MAX_DEG = 240.0
ID_MIN = 0
ID_MAX = 253
HEADER = b"\x55\x55"

# Comandos Hiwonder/LewanSoul usados pelo BusLinker V2.5.
CMD_MOVE_TIME_WRITE = 1
CMD_MOVE_TIME_WAIT_WRITE = 7
CMD_MOVE_START = 11
CMD_MOVE_STOP = 12
CMD_ID_WRITE = 13
CMD_POS_READ = 28
CMD_VIN_READ = 27
CMD_TEMP_READ = 26
CMD_ID_READ = 14

# Use nomes estáveis do robô aqui, sem depender do ID físico.
SERVO_IDENTIFIERS: Dict[int, str] = {
    # 1: "quadril_esquerdo",
    # 2: "joelho_esquerdo",
}


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def deg_to_ticks(angle_deg: float) -> int:
    if not math.isfinite(angle_deg) or not ANGLE_MIN_DEG <= angle_deg <= ANGLE_MAX_DEG:
        raise ValueError("Angulo deve ser finito e estar entre 0 e 240 graus.")
    return int(round(angle_deg * 1000.0 / 240.0))


def ticks_to_deg(ticks: int) -> float:
    return ticks * 240.0 / 1000.0


def calc_checksum(body: bytes) -> int:
    return (~sum(body)) & 0xFF


def build_packet(servo_id: int, command: int, params: bytes = b"") -> bytes:
    if servo_id != 254 or command not in (CMD_MOVE_START, CMD_MOVE_STOP):
        validate_id(servo_id)
    length = len(params) + 3
    body = bytes([servo_id, length, command]) + params
    return HEADER + body + bytes([calc_checksum(body)])


def validate_id(servo_id: int) -> None:
    if type(servo_id) is not int or not ID_MIN <= servo_id <= ID_MAX:
        raise ValueError(f"ID deve estar entre {ID_MIN} e {ID_MAX}: {servo_id}")


@dataclass(frozen=True)
class ServoState:
    servo_id: int
    identifier: str
    angle_deg: float
    voltage_v: float
    velocity_dps: float
    communication_ok: bool = True
    temperature_c: float = math.nan
    position_time_s: float = math.nan


@dataclass(frozen=True)
class ReadResult:
    ok: bool
    params: bytes = b""
    raw: bytes = b""
    error: str = ""


class LX225Bus:
    """Driver serial mínimo para um barramento com vários LX-225."""

    def __init__(
        self,
        port: str,
        baudrate: int = BAUDRATE,
        timeout: float = 0.005,
    ):
        self.port = port
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            write_timeout=0.2,
        )
        time.sleep(0.25)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self._last_angle: Dict[int, Tuple[float, float]] = {}

    def close(self) -> None:
        if self.ser.is_open:
            self.ser.close()

    def __enter__(self) -> "LX225Bus":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def _write(self, servo_id: int, command: int, params: bytes = b"") -> bytes:
        packet = build_packet(servo_id, command, params)
        if self.ser.write(packet) != len(packet):
            raise serial.SerialTimeoutException("Escrita serial incompleta.")
        self.ser.flush()
        return packet

    def _collect(self, deadline_s: float) -> bytes:
        deadline = time.monotonic() + deadline_s
        data = bytearray()

        while time.monotonic() < deadline:
            if self.ser.in_waiting:
                data.extend(self.ser.read(self.ser.in_waiting))
            else:
                time.sleep(0.001)

        if self.ser.in_waiting:
            data.extend(self.ser.read(self.ser.in_waiting))
        return bytes(data)

    @staticmethod
    def _parse_full_packets(raw: bytes) -> List[Tuple[int, int, bytes]]:
        packets = []
        index = 0

        while index <= len(raw) - 6:
            if raw[index:index + 2] != HEADER:
                index += 1
                continue

            length = raw[index + 3]
            total = length + 3
            if total < 6 or index + total > len(raw):
                index += 1
                continue

            packet = raw[index:index + total]
            body = packet[2:-1]
            if calc_checksum(body) == packet[-1]:
                packets.append((packet[2], packet[4], packet[5:-1]))
                index += total
            else:
                index += 1

        return packets

    def read_command(
        self,
        servo_id: int,
        command: int,
        expected_param_len: int,
    ) -> ReadResult:
        validate_id(servo_id)
        self.ser.reset_input_buffer()
        if expected_param_len <= 0:
            raise ValueError("A leitura exige parametros de resposta.")
        self._write(servo_id, command)
        deadline = time.monotonic() + READ_TIMEOUT_S
        raw = bytearray()
        while time.monotonic() < deadline:
            waiting = self.ser.in_waiting
            if not waiting:
                time.sleep(0.001)
                continue
            raw.extend(self.ser.read(waiting))
            for response_id, response_command, params in self._parse_full_packets(raw):
                if (response_id == servo_id and response_command == command
                        and len(params) == expected_param_len):
                    return ReadResult(True, bytes(params), bytes(raw))

        return ReadResult(
            False,
            raw=bytes(raw),
            error=f"Sem resposta válida do ID {servo_id}, comando {command}",
        )

    def read_voltage_v(self, servo_id: int) -> float:
        result = self.read_command(servo_id, CMD_VIN_READ, 2)
        if not result.ok:
            raise TimeoutError(result.error)
        return struct.unpack("<H", result.params)[0] / 1000.0

    def read_angle_deg(self, servo_id: int) -> float:
        result = self.read_command(servo_id, CMD_POS_READ, 2)
        if not result.ok:
            raise TimeoutError(result.error)
        return ticks_to_deg(struct.unpack("<h", result.params)[0])

    def read_temperature_c(self, servo_id: int) -> float:
        result = self.read_command(servo_id, CMD_TEMP_READ, 1)
        if not result.ok:
            raise TimeoutError(result.error)
        return float(result.params[0])

    def read_id(self, servo_id: int) -> int:
        result = self.read_command(servo_id, CMD_ID_READ, 1)
        if not result.ok:
            raise TimeoutError(result.error)
        return result.params[0]

    def read_position_limits(self, servo_id: int) -> Tuple[float, float]:
        result = self.read_command(servo_id, 21, 4)
        if not result.ok:
            raise TimeoutError(result.error)
        lower, upper = struct.unpack('<HH', result.params)
        if not 0 <= lower < upper <= 1000:
            raise ValueError('Limites de posicao invalidos recebidos do servo.')
        return ticks_to_deg(lower), ticks_to_deg(upper)

    def read_mode(self, servo_id: int) -> int:
        result = self.read_command(servo_id, 30, 4)
        if not result.ok:
            raise TimeoutError(result.error)
        return result.params[0]

    def read_torque_enabled(self, servo_id: int) -> bool:
        result = self.read_command(servo_id, 32, 1)
        if not result.ok:
            raise TimeoutError(result.error)
        if result.params[0] not in (0, 1):
            raise ValueError('Estado de torque invalido recebido do servo.')
        return bool(result.params[0])

    def move_verified(self, servo_id: int, angle_deg: float, move_time_s: float) -> None:
        """Move diretamente, confere o alvo e habilita torque se necessario.

        Pode movimentar imediatamente. O chamador deve validar alimentacao,
        modo e limites antes de usar e tentar parar em caso de falha.
        """
        expected = self._move_params(angle_deg, move_time_s)
        self.move(servo_id, angle_deg, move_time_s)
        result = self.read_command(servo_id, 2, 4)
        if not result.ok:
            raise TimeoutError(result.error)
        if result.params != expected:
            raise ValueError(f'ID {servo_id}: o servo nao confirmou o alvo e tempo enviados.')
        if not self.read_torque_enabled(servo_id):
            # Habilita somente depois de confirmar o novo alvo, evitando ativar
            # torque com um alvo antigo desconhecido.
            self._write(servo_id, 31, b'\x01')
            if not self.read_torque_enabled(servo_id):
                raise ValueError(f'ID {servo_id}: torque continua desabilitado; verifique alimentacao e protecoes.')

    def read_offset(self, servo_id: int) -> int:
        result = self.read_command(servo_id, 19, 1)
        if not result.ok:
            raise TimeoutError(result.error)
        return struct.unpack('<b', result.params)[0]

    def set_offset(self, servo_id: int, ticks: int, *, save: bool = False) -> None:
        """Define offset absoluto em passos de 0.24 grau; pode mover o eixo."""
        validate_id(servo_id)
        if type(ticks) is not int or not -125 <= ticks <= 125:
            raise ValueError('Offset deve ser inteiro entre -125 e 125.')
        self._write(servo_id, 17, struct.pack('<b', ticks))
        time.sleep(0.05)
        if self.read_offset(servo_id) != ticks:
            raise ValueError('Offset temporario nao confirmado; nao foi salvo.')
        if save:
            self._write(servo_id, 18)
            time.sleep(0.25)
            if self.read_offset(servo_id) != ticks:
                raise ValueError('Offset divergente apos comando de gravacao.')

    def read_servo(
        self,
        servo_id: int,
        identifier: Optional[str] = None,
    ) -> ServoState:
        """Le posicao, tensao, temperatura e estima velocidade em graus/segundo."""
        validate_id(servo_id)
        angle = self.read_angle_deg(servo_id)
        now = time.monotonic()
        voltage = self.read_voltage_v(servo_id)
        temperature = self.read_temperature_c(servo_id)
        previous = self._last_angle.get(servo_id)
        velocity = math.nan

        if previous is not None:
            previous_time, previous_angle = previous
            elapsed = now - previous_time
            if elapsed > 1e-6:
                velocity = (angle - previous_angle) / elapsed

        self._last_angle[servo_id] = (now, angle)
        return ServoState(
            servo_id=servo_id,
            identifier=identifier or SERVO_IDENTIFIERS.get(
                servo_id, f"servo_{servo_id}"
            ),
            angle_deg=angle,
            voltage_v=voltage,
            velocity_dps=velocity,
            temperature_c=temperature,
            position_time_s=now,
        )

    def move(
        self,
        servo_id: int,
        angle_deg: float,
        move_time_s: float,
    ) -> None:
        """Move um servo para o ângulo informado no tempo indicado."""
        validate_id(servo_id)
        params = self._move_params(angle_deg, move_time_s)
        self.ser.reset_input_buffer()
        self._write(
            servo_id,
            CMD_MOVE_TIME_WRITE,
            params,
        )

    def move_at_speed(
        self,
        servo_id: int,
        angle_deg: float,
        velocity_dps: float,
    ) -> None:
        """Move com velocidade aproximada em graus/segundo."""
        deg_to_ticks(angle_deg)
        if not math.isfinite(velocity_dps) or velocity_dps <= 0:
            raise ValueError("A velocidade deve ser maior que zero.")
        current_angle = self.read_angle_deg(servo_id)
        move_time_s = abs(angle_deg - current_angle) / velocity_dps
        self.move(servo_id, angle_deg, move_time_s)

    @staticmethod
    def _move_params(angle_deg: float, move_time_s: float) -> bytes:
        ticks = deg_to_ticks(angle_deg)
        if not math.isfinite(move_time_s) or not 0 <= move_time_s <= 30:
            raise ValueError("Tempo deve ser finito e estar entre 0 e 30 segundos.")
        return struct.pack("<HH", ticks, round(move_time_s * 1000))

    def prepare_move(self, servo_id: int, angle_deg: float, move_time_s: float) -> None:
        validate_id(servo_id)
        self._write(servo_id, CMD_MOVE_TIME_WAIT_WRITE,
                    self._move_params(angle_deg, move_time_s))

    def start(self, servo_ids: Iterable[int], *, synchronized: bool = False) -> None:
        ids = list(servo_ids)
        for servo_id in ids:
            validate_id(servo_id)
        if synchronized and ids:
            # Broadcast inicia TODOS os movimentos pendentes no barramento.
            self._write(254, CMD_MOVE_START)
        else:
            for servo_id in ids:
                self._write(servo_id, CMD_MOVE_START)

    def move_many(self, targets: Iterable[Tuple[int, float, float]], *,
                  synchronized: bool = False) -> None:
        """Valida todo o lote antes de enviar. Broadcast e opcional."""
        prepared = []
        seen = set()
        for servo_id, angle, duration in targets:
            validate_id(servo_id)
            if servo_id in seen:
                raise ValueError("IDs repetidos no lote.")
            seen.add(servo_id)
            prepared.append((servo_id, self._move_params(angle, duration)))
        for servo_id, params in prepared:
            self._write(servo_id, CMD_MOVE_TIME_WAIT_WRITE, params)
        self.start([servo_id for servo_id, _ in prepared], synchronized=synchronized)

    def move_group_direct(self, targets: Iterable[Tuple[int, float, float]]) -> None:
        """Envia alvos diretos em sequencia rapida e depois confere cada um.

        Os inicios tem pequena defasagem, sem preparo nem broadcast.
        O chamador deve conferir limites/torque e parar o grupo em falha.
        """
        prepared = []
        seen = set()
        for sid, angle, duration in targets:
            validate_id(sid)
            if sid in seen:
                raise ValueError('IDs repetidos no lote.')
            seen.add(sid)
            prepared.append((sid, self._move_params(angle, duration)))
        for sid, params in prepared:
            self._write(sid, CMD_MOVE_TIME_WRITE, params)
        for sid, params in prepared:
            result = self.read_command(sid, 2, 4)
            if not result.ok or result.params != params:
                raise ValueError(f'ID {sid}: alvo direto nao confirmado apos envio ao grupo.')
            if not self.read_torque_enabled(sid):
                raise ValueError(f'ID {sid}: torque desabilitado durante movimento do grupo.')

    def move_many_verified(self, targets: Iterable[Tuple[int, float, float]]) -> None:
        """Confere todos os alvos preparados antes de iniciar por broadcast.

        Exige barramento dedicado: o inicio afeta todos os alvos pendentes.
        Em falha de preparo, reinicie a alimentacao antes de tentar novamente.
        """
        prepared = []
        seen = set()
        for sid, angle, duration in targets:
            validate_id(sid)
            if sid in seen:
                raise ValueError('IDs repetidos no lote.')
            seen.add(sid)
            prepared.append((sid, self._move_params(angle, duration)))
        for sid, params in prepared:
            self._write(sid, CMD_MOVE_TIME_WAIT_WRITE, params)
            result = self.read_command(sid, 8, 4)
            if not result.ok or result.params != params:
                raise ValueError(f'ID {sid}: alvo sincronizado nao confirmado; inicio nao enviado. '
                                 'Reinicie a alimentacao antes de outro teste sincronizado para limpar alvos pendentes.')
        self.start([sid for sid, _ in prepared], synchronized=True)

    def stop(self, servo_id: int) -> None:
        validate_id(servo_id)
        self._write(servo_id, CMD_MOVE_STOP)

    def write_id(self, current_id: int, new_id: int) -> None:
        """Altera e verifica o ID. Conecte somente o servo a reconfigurar."""
        validate_id(current_id)
        validate_id(new_id)
        if current_id == new_id:
            raise ValueError("O novo ID deve ser diferente do ID atual.")
        if self.read_id(current_id) != current_id:
            raise ValueError("O servo nao confirmou o ID atual.")
        try:
            self.read_id(new_id)
        except TimeoutError:
            pass
        else:
            raise ValueError("O novo ID ja responde no barramento.")
        self._write(current_id, CMD_ID_WRITE, bytes([new_id]))
        self._last_angle.pop(current_id, None)
        self._last_angle.pop(new_id, None)
        time.sleep(0.25)
        try:
            verified = self.read_id(new_id)
        except TimeoutError as exc:
            raise TimeoutError("ID enviado, mas sem confirmacao. Verifique os dois IDs antes de repetir.") from exc
        if verified != new_id:
            raise ValueError("Resposta nao confirmou o novo ID; verifique o servo.")

    def scan_ids(self) -> List[int]:
        """Consulta cada ID individualmente, sem movimento nem broadcast.

        Retorna IDs que confirmam seu proprio endereco. Falhas da porta
        interrompem a busca; IDs sem resposta sao ignorados.
        """
        found = []
        for servo_id in range(ID_MIN, ID_MAX + 1):
            try:
                if self.read_id(servo_id) == servo_id:
                    found.append(servo_id)
            except TimeoutError:
                continue
        return found


__all__ = [
    "LX225Bus",
    "SERVO_IDENTIFIERS",
    "ServoState",
    "build_packet",
    "deg_to_ticks",
    "ticks_to_deg",
]


import argparse
import csv
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path

import serial

COMMANDS = {'monitor', 'calibrate', 'add-id', 'list-ids', 'change-id', 'offset'}
FIELDS = ['time_s', 'servo_id', 'identifier', 'angle_deg', 'voltage_v',
          'velocity_dps', 'temperature_c', 'target_deg', 'error_deg', 'status']


def load_registry(path):
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('Cadastro deve ser um objeto JSON de ID para nome.')
    for key, name in data.items():
        validate_id(int(key))
        if str(int(key)) != key or not isinstance(name, str) or not name.strip():
            raise ValueError('ID ou nome invalido no cadastro.')
    return data


def save_registry(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)


class Recorder:
    def __init__(self, folder, live=False):
        import matplotlib
        if not live:
            matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        self.plt = plt
        self.folder = Path(folder) / datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        self.folder.mkdir(parents=True)
        self.file = (self.folder / 'telemetria.csv').open('w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=FIELDS)
        self.writer.writeheader()
        self.rows = []
        self.start = time.monotonic()
        self.live = live
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        if live:
            plt.ion()
            plt.show(block=False)

    def add(self, state, target=math.nan, status='ok'):
        stamp = state.position_time_s
        row = dict(time_s=stamp-self.start, servo_id=state.servo_id,
                   identifier=state.identifier, angle_deg=state.angle_deg,
                   voltage_v=state.voltage_v, velocity_dps=state.velocity_dps,
                   temperature_c=state.temperature_c, target_deg=target,
                   error_deg=state.angle_deg-target, status=status)
        self.rows.append(row)
        self.writer.writerow(row)
        self.file.flush()

    def failure(self, sid, exc):
        row = dict.fromkeys(FIELDS, math.nan)
        row.update(time_s=time.monotonic()-self.start, servo_id=sid,
                   identifier=f'servo_{sid}', status=str(exc))
        self.rows.append(row)
        self.writer.writerow(row)
        self.file.flush()

    def draw(self):
        metrics = [('angle_deg', 'Posicao (graus)'), ('velocity_dps', 'Velocidade estimada (graus/s)'),
                   ('voltage_v', 'Tensao (V)'), ('temperature_c', 'Temperatura (C)')]
        for ax, (field, title) in zip(self.axes.flat, metrics):
            ax.clear()
            for sid in sorted({r['servo_id'] for r in self.rows}):
                rows = [r for r in self.rows if r['servo_id'] == sid]
                ax.plot([r['time_s'] for r in rows], [r[field] for r in rows], label=f'ID {sid}')
                if field == 'angle_deg' and any(math.isfinite(r['target_deg']) for r in rows):
                    ax.step([r['time_s'] for r in rows], [r['target_deg'] for r in rows],
                            where='post', linestyle='--', label=f'Alvo {sid}')
            ax.set(xlabel='Tempo (s)', ylabel=title)
            ax.grid(True, alpha=0.3)
            if self.rows:
                ax.legend()
        self.fig.tight_layout()
        if self.live:
            self.plt.pause(0.001)

    def close(self):
        self.file.close()
        self.draw()
        self.fig.savefig(self.folder / 'graficos.png', dpi=160)
        self.plt.close(self.fig)
        print(f'CSV e graficos: {self.folder.resolve()}')


def check_state(state, max_temp):
    if not 6 <= state.voltage_v <= 8.4:
        raise ValueError(f'ID {state.servo_id}: tensao fora de 6 a 8.4 V.')
    if not math.isfinite(state.temperature_c) or state.temperature_c >= max_temp:
        raise ValueError(f'ID {state.servo_id}: limite de temperatura {max_temp} C.')


def stop_all(bus, ids):
    for sid in ids:
        try:
            bus.stop(sid)
        except (serial.SerialException, OSError) as exc:
            print(f'Nao foi possivel parar ID {sid}: {exc}', file=sys.stderr)


def sample(bus, ids, names, rec, targets=None, max_temp=60, strict=False):
    states = []
    for sid in ids:
        try:
            state = bus.read_servo(sid, names.get(str(sid)))
        except TimeoutError as exc:
            rec.failure(sid, exc)
            print(f'ID {sid}: {exc}', file=sys.stderr)
            if strict:
                raise
            continue
        rec.add(state, (targets or {}).get(sid, math.nan))
        print(f'ID {sid}: {state.angle_deg:.2f} graus | {state.velocity_dps:.2f} graus/s | '
              f'{state.voltage_v:.2f} V | {state.temperature_c:.0f} C')
        if strict:
            check_state(state, max_temp)
        states.append(state)
    if rec.live:
        rec.draw()
    return states


def calibrate(bus, args, ids, names, rec):
    initial = sample(bus, ids, names, rec, max_temp=args.max_temp, strict=True)
    # Prevalida todos os alvos antes de qualquer movimento.
    plans = [{s.servo_id: ticks_to_deg(deg_to_ticks(s.angle_deg + delta))
              for s in initial} for delta in args.deltas]
    results = []
    try:
        for targets in plans:
            bus.move_many([(sid, angle, args.seconds) for sid, angle in targets.items()])
            end = time.monotonic() + args.seconds + args.settle
            while time.monotonic() < end:
                sample(bus, ids, names, rec, targets, args.max_temp, strict=True)
                time.sleep(args.interval)
            samples = []
            for _ in range(args.samples):
                samples.extend(sample(bus, ids, names, rec, targets, args.max_temp, strict=True))
                time.sleep(args.interval)
            for sid in ids:
                values = [s.angle_deg for s in samples if s.servo_id == sid]
                mean = sum(values)/len(values)
                error = mean-targets[sid]
                results.append(dict(servo_id=sid, target_deg=targets[sid], measured_mean_deg=mean,
                                    error_deg=error, spread_deg=max(values)-min(values),
                                    passed=abs(error) <= args.tolerance))
    finally:
        stop_all(bus, ids)
        path = rec.folder / 'calibracao.csv'
        with path.open('w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['servo_id', 'target_deg', 'measured_mean_deg',
                                                      'error_deg', 'spread_deg', 'passed'])
            writer.writeheader()
            writer.writerows(results)
    for row in results:
        print(row)
    return 0 if all(r['passed'] for r in results) else 2


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    for command in sorted(COMMANDS):
        sp = sub.add_parser(command)
        sp.add_argument('--registry', type=Path, default=Path('servos.json'))
        if command not in ('add-id', 'list-ids'):
            sp.add_argument('--port', required=True)
        if command == 'add-id':
            sp.add_argument('--id', type=int, required=True)
            sp.add_argument('--name', required=True)
        if command == 'change-id':
            sp.add_argument('--from-id', type=int, required=True)
            sp.add_argument('--to-id', type=int, required=True)
            sp.add_argument('--single-servo', action='store_true', required=True,
                            help='Declara que somente o servo a alterar esta conectado')
        if command == 'offset':
            sp.add_argument('--id', type=int, required=True)
            sp.add_argument('--ticks', type=int, help='Offset absoluto -125..125; cada passo = 0.24 grau')
            sp.add_argument('--save', action='store_true', help='Grava o offset na memoria permanente')
        if command in ('monitor', 'calibrate'):
            sp.add_argument('--ids', nargs='+', type=int, help='Omitir para usar todos os IDs cadastrados')
            sp.add_argument('--interval', type=float, default=0.1)
            sp.add_argument('--output', type=Path, default=Path('resultados'))
            sp.add_argument('--live', action='store_true', help='Mostra graficos durante a coleta')
        if command == 'monitor':
            sp.add_argument('--duration', type=float, default=30)
        if command == 'calibrate':
            sp.add_argument('--deltas', nargs='+', type=float, default=[-5, 0, 5, 0],
                            help='Deslocamentos relativos a posicao inicial, em graus')
            sp.add_argument('--seconds', type=float, default=2)
            sp.add_argument('--settle', type=float, default=0.5)
            sp.add_argument('--samples', type=int, default=5)
            sp.add_argument('--tolerance', type=float, default=2)
            sp.add_argument('--max-temp', type=float, default=60)
    return p


def tools_main(bus_class):
    args = parser().parse_args()
    try:
        names = load_registry(args.registry)
        if args.command == 'add-id':
            validate_id(args.id)
            if not args.name.strip():
                raise ValueError('Nome nao pode ser vazio.')
            names[str(args.id)] = args.name.strip()
            save_registry(args.registry, names)
            print(f'ID {args.id} cadastrado como {args.name}. O ID fisico nao foi alterado.')
            return 0
        if args.command == 'list-ids':
            print(json.dumps(names, ensure_ascii=False, indent=2))
            return 0
        if args.command == 'change-id':
            validate_id(args.from_id)
            validate_id(args.to_id)
            if str(args.to_id) in names:
                raise ValueError('ID de destino ja cadastrado; escolha outro ID.')
            with bus_class(args.port) as bus:
                bus.write_id(args.from_id, args.to_id)
            print(f'ID fisico confirmado: {args.to_id}')
            names[str(args.to_id)] = names.pop(str(args.from_id), f'servo_{args.to_id}')
            save_registry(args.registry, names)
            return 0
        if args.command == 'offset':
            validate_id(args.id)
            if args.save and args.ticks is None:
                raise ValueError('--save exige --ticks explicito.')
            if args.ticks is not None and not -125 <= args.ticks <= 125:
                raise ValueError('Ticks devem estar entre -125 e 125.')
            with bus_class(args.port) as bus:
                old = bus.read_offset(args.id)
                print(f'Offset anterior: {old} ticks ({old*0.24:.2f} graus). Anote para restaurar.')
                if args.ticks is not None:
                    print('Aplicando offset absoluto; o eixo pode se mover.')
                    bus.set_offset(args.id, args.ticks, save=args.save)
                    print(f'Offset confirmado: {args.ticks}. Gravacao permanente solicitada: {args.save}.')
            return 0
        ids = args.ids if args.ids is not None else [int(k) for k in names]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError('Informe IDs unicos ou cadastre-os com add-id.')
        for sid in ids:
            validate_id(sid)
        if not math.isfinite(args.interval) or args.interval < 0.01:
            raise ValueError('Intervalo deve ser finito e >= 0.01 s.')
        if args.command == 'monitor':
            if not math.isfinite(args.duration) or args.duration <= 0:
                raise ValueError('Duracao deve ser finita e positiva.')
        else:
            for value, low, high in [(args.seconds, 0.5, 30), (args.settle, 0, 30),
                                     (args.tolerance, 0, 240), (args.max_temp, 1, 85)]:
                if not math.isfinite(value) or not low <= value <= high:
                    raise ValueError('Tempo, tolerancia ou temperatura fora dos limites.')
            if not 1 <= args.samples <= 100:
                raise ValueError('Use 1 a 100 amostras.')
            if any(not math.isfinite(v) or abs(v) > 10 for v in args.deltas):
                raise ValueError('Cada delta deve estar entre -10 e 10 graus.')
        rec = Recorder(args.output, args.live)
        try:
            with bus_class(args.port) as bus:
                if args.command == 'calibrate':
                    return calibrate(bus, args, ids, names, rec)
                end = time.monotonic() + args.duration
                while time.monotonic() < end:
                    sample(bus, ids, names, rec)
                    time.sleep(args.interval)
                return 0 if rec.rows and all(r['status'] == 'ok' for r in rec.rows) else 1
        finally:
            rec.close()
    except (ValueError, TimeoutError, serial.SerialException, OSError, ImportError) as exc:
        print(f'Falha: {exc}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('Interrompido. Dados coletados foram preservados.', file=sys.stderr)
        return 130


import argparse
import math
import sys
import time

import serial
from serial.tools import list_ports


def select_port(port):
    if port:
        return port
    ports = sorted(list_ports.comports(), key=lambda item: item.device)
    usb_ports = [item for item in ports if item.vid is not None]
    if len(usb_ports) == 1:
        selected = usb_ports[0]
        print(f'Porta USB selecionada: {selected.device} - {selected.description}', flush=True)
        return selected.device
    available = ', '.join(f'{item.device} ({item.description})' for item in ports) or 'nenhuma'
    reason = 'Mais de uma porta USB encontrada' if usb_ports else 'Nenhuma porta serial USB encontrada'
    raise ValueError(f'{reason}. Informe --port COMx. Portas disponiveis: {available}.')


def show_states(bus, ids):
    states = []
    print('ID | Posicao (graus) | Tensao (V) | Temperatura (C)')
    for sid in ids:
        try:
            state = bus.read_servo(sid)
            states.append(state)
            print(f'{state.servo_id:3} | {state.angle_deg:15.2f} | {state.voltage_v:10.2f} | {state.temperature_c:15.1f}')
        except TimeoutError as exc:
            print(f'Falha na leitura do ID {sid}: {exc}', file=sys.stderr)
    return states


def discover_servos(bus):
    print('Buscando IDs de 0 a 253 (cerca de 12 segundos)...', flush=True)
    ids = bus.scan_ids()
    print(f'Quantidade de IDs encontrados: {len(ids)}', flush=True)
    print('IDs encontrados: ' + (', '.join(map(str, ids)) or 'nenhum'), flush=True)
    print('Servos com IDs repetidos nao podem ser contados separadamente.', flush=True)
    if not ids:
        print('Nenhum servo respondeu. Confira alimentacao, conexoes e modo da BusLinker.', file=sys.stderr)
    return ids


def test_movement(bus, states, delta, seconds, synchronized=False):
    if not states or len({s.servo_id for s in states}) != len(states):
        raise ValueError('Selecione IDs distintos para movimentar.')
    if not math.isfinite(delta) or abs(delta) > 100:
        raise ValueError('Delta deve estar entre -100 e 100 graus.')
    if not math.isfinite(seconds) or not 0.5 <= seconds <= 30:
        raise ValueError('Tempo deve estar entre 0.5 e 30 segundos.')
    targets = [(s.servo_id, s.angle_deg + delta, seconds) for s in states]
    needs_torque = []
    for sid, angle, duration in targets:
        if not math.isfinite(angle) or not 0 <= angle <= 240:
            raise ValueError(f'ID {sid}: alvo {angle:.2f} graus fora de 0 a 240. Reduza o deslocamento ou inverta o sentido.')
        bus._move_params(angle, duration)
    if any(not 6 <= s.voltage_v <= 8.4 for s in states):
        raise ValueError('Tensao lida fora de 6 a 8.4 V.')
    for sid, angle, duration in targets:
        if bus.read_mode(sid) != 0:
            raise ValueError(f'ID {sid}: nao esta em modo de posicao.')
        lower, upper = bus.read_position_limits(sid)
        if not lower <= angle <= upper:
            raise ValueError(f'ID {sid}: alvo {angle:.2f} fora dos limites internos {lower:.2f} a {upper:.2f} graus.')
        if (synchronized or len(states) > 1) and not bus.read_torque_enabled(sid):
            current = next(state.angle_deg for state in states if state.servo_id == sid)
            if not lower <= current <= upper:
                raise ValueError(f'ID {sid}: posicao atual fora dos limites; nao e possivel habilitar torque aqui.')
            needs_torque.append((sid, current))
        print(f'ID {sid}: alvo {angle:.2f} graus em {duration:.2f} s; limites {lower:.2f} a {upper:.2f}.', flush=True)
    try:
        for sid, current in needs_torque:
            print(f'ID {sid}: habilitando torque na posicao atual.', flush=True)
            bus.move_verified(sid, current, 0.5)
        if synchronized:
            bus.move_many_verified(targets)
        elif len(states) > 1:
            print('Enviando movimentos diretos em sequencia rapida aos IDs selecionados.', flush=True)
            bus.move_group_direct(targets)
        else:
            for sid, angle, duration in targets:
                bus.move_verified(sid, angle, duration)
        end = time.monotonic() + seconds + 0.5
        while time.monotonic() < end:
            for state in states:
                measured = bus.read_servo(state.servo_id)
                print(measured)
                if not 6 <= measured.voltage_v <= 8.4:
                    raise ValueError(
                        f'ID {measured.servo_id}: tensao {measured.voltage_v:.3f} V '
                        'fora de 6 a 8.4 V durante o movimento. Teste interrompido; '
                        'confira fonte, limite de corrente, cabos e conexoes antes de repetir.'
                    )
            time.sleep(0.1)
    finally:
        for state in states:
            try:
                bus.stop(state.servo_id)
            except (serial.SerialException, OSError) as exc:
                print(f'Falha ao parar ID {state.servo_id}: {exc}', file=sys.stderr)


def interactive_menu(bus, ids):
    print('\nTeste de movimento: deixe o eixo livre. Cada movimento parte da posicao atual.')
    while True:
        print('\n1 - Ler posicao, tensao e temperatura')
        print('2 - Mover servo (alterar deslocamento e tempo)')
        print('3 - Buscar IDs novamente')
        print('4 - Mover varios servos juntos (inicio em sequencia rapida)')
        print('0 - Sair')
        try:
            choice = input('Opcao: ').strip()
            if choice == '0':
                return 0
            if choice == '1':
                show_states(bus, ids)
            elif choice == '3':
                ids = discover_servos(bus)
                show_states(bus, ids)
            elif choice == '4':
                if len(ids) < 2:
                    print('Sao necessarios pelo menos dois IDs. Conecte os servos e busque pela opcao 3.')
                    continue
                defaults = ' '.join(map(str, ids))
                raw = input(f'IDs separados por espaco [{defaults}]: ').strip() or defaults
                selected = [int(value) for value in raw.replace(',', ' ').split()]
                if len(selected) < 2 or len(set(selected)) != len(selected):
                    raise ValueError('Selecione pelo menos dois IDs distintos.')
                if any(sid not in ids for sid in selected):
                    raise ValueError('Escolha IDs encontrados ou busque novamente pela opcao 3.')
                print('Os servos recebem comandos diretos, com pequena diferenca no instante de inicio.')
                delta = float((input('Deslocamento para todos em graus (-100 a +100) [5]: ').strip() or '5').replace(',', '.'))
                seconds = float((input('Tempo para todos em segundos (0.5 a 30) [2]: ').strip() or '2').replace(',', '.'))
                states = [bus.read_servo(sid) for sid in selected]
                test_movement(bus, states, delta, seconds)
                show_states(bus, selected)
            elif choice == '2':
                if not ids:
                    print('Busque os IDs pela opcao 3 antes de mover.')
                    continue
                default = str(ids[0]) if len(ids) == 1 else ''
                raw = input(f'ID do servo{f" [{default}]" if default else ""}: ').strip()
                sid = int(raw or default)
                if sid not in ids:
                    raise ValueError('Escolha um ID encontrado ou busque novamente pela opcao 3.')
                delta = float((input('Deslocamento em graus (-100 a +100) [5]: ').strip() or '5').replace(',', '.'))
                seconds = float((input('Tempo em segundos (0.5 a 30) [2]: ').strip() or '2').replace(',', '.'))
                # Consulta fresca antes de calcular o alvo; nunca usa a posicao antiga da busca.
                state = bus.read_servo(sid)
                test_movement(bus, [state], delta, seconds)
                show_states(bus, [sid])
            else:
                print('Opcao invalida.')
        except (ValueError, TimeoutError) as exc:
            print(f'Falha: {exc}', file=sys.stderr)
        except EOFError:
            return 0


def main(bus_class=LX225Bus):
    if len(sys.argv) > 1 and sys.argv[1] in COMMANDS:
        return tools_main(bus_class)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.epilog = 'Comandos adicionais: monitor, calibrate, add-id, list-ids, change-id, offset. Use COMANDO --help.'
    parser.add_argument('--port', help='Porta COM; omitida, seleciona a unica serial USB disponivel')
    parser.add_argument('--ids', nargs='+', type=int, help='IDs a consultar; omitidos, busca automaticamente')
    parser.add_argument('--scan', action='store_true', help='Busca todos os IDs e consulta os servos, sem movimento')
    parser.add_argument('--interactive', action='store_true', help='Abre menu para consultar e mover; automatico sem argumentos em terminal')
    parser.add_argument('--move', action='store_true', help='Move +delta a partir da posicao lida')
    parser.add_argument('--delta', type=float, default=5.0, help='Deslocamento relativo de -100 a +100 graus (padrao: 5)')
    parser.add_argument('--seconds', type=float, default=2.0)
    parser.add_argument('--synchronized', action='store_true', help='Inicia TODOS os movimentos pendentes por broadcast')
    args = parser.parse_args()
    try:
        interactive = args.interactive or (len(sys.argv) == 1 and sys.stdin.isatty())
        if args.interactive and (args.scan or args.move):
            raise ValueError('Use --interactive separadamente de --scan e --move.')
        if args.scan and args.ids:
            raise ValueError('Use --scan ou --ids, separadamente.')
        if args.move and (args.scan or not args.ids):
            raise ValueError('Para movimentar, informe --ids explicitamente e remova --scan.')
        for sid in args.ids or []:
            validate_id(sid)
        if args.ids and len(set(args.ids)) != len(args.ids):
            raise ValueError('IDs devem ser diferentes.')
        if not math.isfinite(args.delta) or abs(args.delta) > 100:
            raise ValueError('Delta deve estar entre -100 e 100 graus.')
        if not math.isfinite(args.seconds) or not 0.5 <= args.seconds <= 30:
            raise ValueError('Tempo deve estar entre 0.5 e 30 segundos.')
        args.port = select_port(args.port)
        with bus_class(args.port) as bus:
            print(f'Porta: {args.port}', flush=True)
            if not args.ids:
                args.ids = discover_servos(bus)
                if not args.ids and not interactive:
                    return 1
            states = show_states(bus, args.ids)
            if interactive:
                return interactive_menu(bus, args.ids)
            if len(states) != len(args.ids):
                return 1
            if args.move:
                test_movement(bus, states, args.delta, args.seconds, args.synchronized)
        return 0
    except (ValueError, TimeoutError, serial.SerialException, OSError) as exc:
        print(f'Falha: {exc}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('Teste interrompido.', file=sys.stderr)
        return 130



class BusLinkerV3(LX225Bus):
    """Interface BusLinker V3.0."""


__all__ += ["BusLinkerV3"]


if __name__ == "__main__":
    raise SystemExit(main(bus_class=BusLinkerV3))
