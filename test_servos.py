"""Teste de bancada: leitura por padrao; movimento exige --move."""
import argparse
import math
import sys
import time

import serial
from servo_testbench import LX225Bus, validate_id


def main(bus_class=LX225Bus):
    from bench_tools import COMMANDS, main as tools_main
    if len(sys.argv) > 1 and sys.argv[1] in COMMANDS:
        return tools_main(bus_class)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.epilog = 'Comandos adicionais: monitor, calibrate, add-id, list-ids, change-id, offset. Use COMANDO --help.'
    parser.add_argument('--port', required=True)
    parser.add_argument('--ids', nargs='+', type=int, required=True)
    parser.add_argument('--move', action='store_true', help='Move +delta a partir da posicao lida')
    parser.add_argument('--delta', type=float, default=5.0)
    parser.add_argument('--seconds', type=float, default=2.0)
    parser.add_argument('--synchronized', action='store_true', help='Inicia TODOS os movimentos pendentes por broadcast')
    args = parser.parse_args()
    try:
        for sid in args.ids:
            validate_id(sid)
        if len(set(args.ids)) != len(args.ids):
            raise ValueError('IDs devem ser diferentes.')
        if not math.isfinite(args.delta) or abs(args.delta) > 10:
            raise ValueError('Delta deve estar entre -10 e 10 graus.')
        if not math.isfinite(args.seconds) or not 0.5 <= args.seconds <= 30:
            raise ValueError('Tempo deve estar entre 0.5 e 30 segundos.')
        with bus_class(args.port) as bus:
            states = [bus.read_servo(sid) for sid in args.ids]
            for state in states:
                print(state)
            if args.move:
                targets = [(s.servo_id, s.angle_deg + args.delta, args.seconds) for s in states]
                for sid, angle, duration in targets:
                    bus._move_params(angle, duration)
                if any(not 6 <= s.voltage_v <= 8.4 for s in states):
                    raise ValueError('Tensao lida fora de 6 a 8.4 V.')
                try:
                    bus.move_many(targets, synchronized=args.synchronized)
                    end = time.monotonic() + args.seconds + 0.5
                    while time.monotonic() < end:
                        for sid in args.ids:
                            print(bus.read_servo(sid))
                        time.sleep(0.1)
                finally:
                    for sid in args.ids:
                        try:
                            bus.stop(sid)
                        except (serial.SerialException, OSError) as exc:
                            print(f'Falha ao parar ID {sid}: {exc}', file=sys.stderr)
        return 0
    except (ValueError, TimeoutError, serial.SerialException, OSError) as exc:
        print(f'Falha: {exc}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('Teste interrompido.', file=sys.stderr)
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
