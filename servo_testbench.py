"""Driver compartilhado LX-225 para BusLinker V2.5 e V3."""

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
