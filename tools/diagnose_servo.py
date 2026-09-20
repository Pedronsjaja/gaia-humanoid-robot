"""Diagnostico somente por leitura; nao move nem altera configuracoes."""
import argparse
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import serial
from servo_testbench import LX225Bus, ticks_to_deg, validate_id


def diagnose(bus, sid):
    failed = False
    reads = [
        ('ID confirmado', 14, 'B'),
        ('Posicao (ticks)', 28, 'h'),
        ('Tensao (mV)', 27, 'H'),
        ('Temperatura (C)', 26, 'B'),
        ('Modo (0=posicao, 1=motor), reservado, velocidade', 30, 'BBh'),
        ('Torque habilitado (0=nao, 1=sim)', 32, 'B'),
        ('Limites de posicao (ticks)', 21, 'HH'),
        ('Limites de tensao (mV)', 23, 'HH'),
        ('Temperatura maxima configurada (C)', 25, 'B'),
        ('Ultimo alvo imediato (ticks), tempo (ms)', 2, 'HH'),
        ('Alvo preparado (ticks), tempo (ms)', 8, 'HH'),
    ]
    for name, command, fmt in reads:
        result = bus.read_command(sid, command, struct.calcsize('<' + fmt))
        if not result.ok:
            print(f'{name}: SEM RESPOSTA VALIDA; recebido={result.raw.hex(" ")}', flush=True)
            failed = True
            continue
        values = struct.unpack('<' + fmt, result.params)
        suffix = ''
        if command in (28, 2, 8):
            suffix = f' ({ticks_to_deg(values[0]):.2f} graus)'
        elif command == 21:
            suffix = f' ({ticks_to_deg(values[0]):.2f} a {ticks_to_deg(values[1]):.2f} graus)'
        print(f'{name}: {", ".join(map(str, values))}{suffix}', flush=True)
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', required=True)
    parser.add_argument('--id', type=int, required=True)
    args = parser.parse_args()
    try:
        validate_id(args.id)
        with LX225Bus(args.port) as bus:
            return diagnose(bus, args.id)
    except (ValueError, serial.SerialException, OSError) as exc:
        print(f'Falha: {exc}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
