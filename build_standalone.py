"""Gera os dois arquivos autonomos a partir dos modulos compartilhados."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    driver = (ROOT / 'servo_testbench.py').read_text(encoding='utf-8')
    driver = driver.split('\n', 1)[1]
    bench = (ROOT / 'bench_tools.py').read_text(encoding='utf-8').split('\n', 1)[1]
    bench = bench.replace('from servo_testbench import validate_id, deg_to_ticks, ticks_to_deg\n', '')
    bench = bench.replace('def main(bus_class):', 'def tools_main(bus_class):')
    cli = (ROOT / 'test_servos.py').read_text(encoding='utf-8').split('\n', 1)[1]
    cli = cli.replace('from servo_testbench import LX225Bus, validate_id\n', '')
    cli = cli.replace('    from bench_tools import COMMANDS, main as tools_main\n', '')
    cli = cli.split("\nif __name__ == '__main__':")[0]
    for version, filename, classname in [('2.5', 'buslinker_v2_5.py', 'BusLinkerV2_5'),
                                          ('3.0', 'buslinker_v3.py', 'BusLinkerV3')]:
        header = f'"""BusLinker V{version}: driver, graficos, IDs e calibracao LX-225.\n\n'
        header += 'Arquivo autonomo; dependencias externas: pyserial e matplotlib.\n'
        header += 'Gerado por tools/build_standalone.py; edite os modulos fonte para regenerar.\n"""\n'
        tail = f'\n\nclass {classname}(LX225Bus):\n    """Interface BusLinker V{version}."""\n'
        tail += f'\n\n__all__ += ["{classname}"]\n'
        tail += f'\n\nif __name__ == "__main__":\n    raise SystemExit(main(bus_class={classname}))\n'
        (ROOT / filename).write_text(header + driver + '\n\n' + bench + '\n\n' + cli + tail,
                                    encoding='utf-8')


if __name__ == '__main__':
    build()
