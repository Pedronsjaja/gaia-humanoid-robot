"""Teste de bancada: descoberta, menu interativo e movimento explicito."""
import argparse
import math
import sys
import time

import serial
from serial.tools import list_ports
from servo_testbench import LX225Bus, validate_id


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
    from bench_tools import COMMANDS, main as tools_main
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


if __name__ == '__main__':
    raise SystemExit(main())
