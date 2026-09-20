import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import serial
import servo_testbench as driver
import test_servos as cli
import buslinker_v3 as v3
import buslinker_v2_5 as v25
from test_bench import ServoSerial


class DiscoveryTests(unittest.TestCase):
    def test_scan_finds_5_and_6_using_only_id_reads(self):
        bus = driver.LX225Bus.__new__(driver.LX225Bus)
        bus.ser = ServoSerial()
        bus.ser.ids = {0, 5, 6, 253}
        with patch.object(driver, 'READ_TIMEOUT_S', 0.002):
            self.assertEqual(bus.scan_ids(), [0, 5, 6, 253])
        self.assertEqual({p[4] for p in bus.ser.packets}, {driver.CMD_ID_READ})
        self.assertEqual([p[2] for p in bus.ser.packets], list(range(254)))

    def test_scan_does_not_hide_disconnection(self):
        bus = driver.LX225Bus.__new__(driver.LX225Bus)
        with patch.object(bus, 'read_id', side_effect=serial.SerialException('desconectado')):
            with self.assertRaises(serial.SerialException):
                bus.scan_ids()

    def test_scan_ignores_mismatched_id(self):
        bus = driver.LX225Bus.__new__(driver.LX225Bus)
        with patch.object(bus, 'read_id', return_value=5):
            self.assertEqual(bus.scan_ids(), [5])

    def test_cli_discovery_and_movement_guards_in_all_builds(self):
        port = SimpleNamespace(device='COM7', description='CH343', vid=0x1a86)
        for module in (cli, v3, v25):
            for argv, found, expected in (([], [5, 6], 0), (['--scan'], [], 1),
                                          (['--move'], [5, 6], 1),
                                          (['--scan', '--ids', '5'], [5], 1),
                                          (['--scan', '--move'], [5], 1)):
                with self.subTest(module=module.__name__, argv=argv):
                    factory = MagicMock()
                    bus = factory.return_value.__enter__.return_value
                    bus.scan_ids.return_value = found
                    bus.read_servo.side_effect = lambda sid: driver.ServoState(sid, f'servo_{sid}', 120, 7.4, 0, temperature_c=35)
                    output = io.StringIO()
                    with patch('sys.argv', ['servo.py'] + argv), patch('sys.stdin.isatty', return_value=False), patch.object(module.list_ports, 'comports', return_value=[port]), contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                        self.assertEqual(module.main(factory), expected)
                    bus.move_many.assert_not_called()
                    if expected == 0:
                        self.assertIn('Quantidade de IDs encontrados: 2', output.getvalue())
                        self.assertIn('IDs encontrados: 5, 6', output.getvalue())
                        factory.assert_called_once_with('COM7')
                    elif '--move' in argv or '--ids' in argv:
                        factory.assert_not_called()

    def test_ambiguous_or_bluetooth_ports_require_explicit_selection(self):
        bluetooth = SimpleNamespace(device='COM3', description='Bluetooth', vid=None)
        usb1 = SimpleNamespace(device='COM7', description='CH343', vid=0x1a86)
        usb2 = SimpleNamespace(device='COM8', description='USB Serial', vid=0x1a86)
        for ports in ([], [bluetooth], [bluetooth, usb1, usb2]):
            with patch.object(cli.list_ports, 'comports', return_value=ports):
                with self.assertRaises(ValueError):
                    cli.select_port(None)
                self.assertEqual(cli.select_port('COM7'), 'COM7')


if __name__ == '__main__':
    unittest.main()
