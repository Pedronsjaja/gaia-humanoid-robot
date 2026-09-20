import contextlib
import io
import unittest
from unittest.mock import MagicMock, patch, call

import servo_testbench as driver
import test_servos as cli
import buslinker_v3 as v3
import buslinker_v2_5 as v25


class InteractiveTests(unittest.TestCase):
    def bus(self, angle=150, voltage=7.4):
        bus = MagicMock()
        bus.read_servo.return_value = driver.ServoState(6, 'servo_6', angle, voltage, 0, temperature_c=31)
        bus._move_params.side_effect = driver.LX225Bus._move_params
        bus.read_mode.return_value = 0
        bus.read_position_limits.return_value = (0, 240)
        bus.read_torque_enabled.return_value = True
        return bus

    def test_menu_exit_does_not_move(self):
        for module in (cli, v3, v25):
            bus = self.bus()
            with patch('builtins.input', return_value='0'), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(module.interactive_menu(bus, [6]), 0)
            bus.move_many.assert_not_called()
            bus.stop.assert_not_called()

    def test_menu_uses_fresh_position_and_selected_duration(self):
        for module in (cli, v3, v25):
            bus = self.bus(angle=151.68)
            with patch('builtins.input', side_effect=['2', '', '-5,5', '3', '0']), patch.object(module.time, 'monotonic', side_effect=[0, 4]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(module.interactive_menu(bus, [6]), 0)
            bus.move_verified.assert_called_once_with(6, 146.18, 3.0)
            bus.stop.assert_called_once_with(6)

    def test_invalid_movement_never_writes(self):
        for delta, seconds, angle, voltage in [(101, 2, 100, 7.4), (-101, 2, 150, 7.4), (5, 0, 150, 7.4),
                                               (float('nan'), 2, 150, 7.4),
                                               (100, 2, 151.68, 7.4), (-100, 2, 99, 7.4),
                                               (5, 2, 239, 7.4), (5, 2, 150, 5)]:
            bus = self.bus(angle, voltage)
            with self.assertRaises(ValueError):
                cli.test_movement(bus, [bus.read_servo(6)], delta, seconds)
            bus.move_many.assert_not_called()
            bus.stop.assert_not_called()

    def test_full_displacement_range_in_menu_and_cli(self):
        for module in (cli, v3, v25):
            for delta, angle, target in [(100, 140, 240), (-100, 100, 0)]:
                for interactive in (False, True):
                    with self.subTest(module=module.__name__, delta=delta, interactive=interactive):
                        bus = self.bus(angle=angle)
                        factory = MagicMock()
                        factory.return_value.__enter__.return_value = bus
                        argv = ['servo.py', '--port', 'COM7', '--ids', '6']
                        argv += ['--interactive'] if interactive else ['--move', '--delta', str(delta), '--seconds', '5']
                        with patch('sys.argv', argv), patch('builtins.input', side_effect=['2', '', str(delta), '5', '0']), patch.object(module.time, 'monotonic', side_effect=[0, 6]), contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(module.main(factory), 0)
                        bus.move_verified.assert_called_once_with(6, target, 5.0)
                        bus.stop.assert_called_once_with(6)

    def test_stop_on_telemetry_failure_or_interrupt(self):
        for failure in (TimeoutError('sem resposta'), KeyboardInterrupt()):
            bus = self.bus()
            state = bus.read_servo(6)
            bus.read_servo.side_effect = failure
            with patch.object(cli.time, 'monotonic', return_value=0):
                with self.assertRaises(type(failure)):
                    cli.test_movement(bus, [state], 5, 2)
            bus.stop.assert_called_once_with(6)

    def test_servo_limits_and_mode_checked_before_movement(self):
        for mode, limits, delta in [(1, (30, 210), 5), (0, (30, 210), 80)]:
            bus = self.bus()
            bus.read_mode.return_value = mode
            bus.read_position_limits.return_value = limits
            with self.assertRaises(ValueError):
                cli.test_movement(bus, [bus.read_servo(6)], delta, 2)
            bus.move_verified.assert_not_called()
            bus.move_many.assert_not_called()

    def test_stop_when_target_confirmation_fails(self):
        bus = self.bus()
        bus.move_verified.side_effect = TimeoutError('alvo nao confirmado')
        with self.assertRaises(TimeoutError):
            cli.test_movement(bus, [bus.read_servo(6)], 5, 2)
        bus.stop.assert_called_once_with(6)

    def test_rescan_after_empty_scan_does_not_move(self):
        bus = self.bus()
        bus.scan_ids.return_value = [6]
        output = io.StringIO()
        with patch('builtins.input', side_effect=['2', '3', '0']), contextlib.redirect_stdout(output):
            self.assertEqual(cli.interactive_menu(bus, []), 0)
        self.assertIn('IDs encontrados: 6', output.getvalue())
        bus.move_many.assert_not_called()

    def test_no_args_in_terminal_opens_menu(self):
        for module in (cli, v3, v25):
            factory = MagicMock()
            factory.return_value.__enter__.return_value = self.bus()
            factory.return_value.__enter__.return_value.scan_ids.return_value = [6]
            output = io.StringIO()
            with patch('sys.argv', ['servo.py']), patch('sys.stdin.isatty', return_value=True), patch.object(module, 'select_port', return_value='COM7'), patch('builtins.input', return_value='0'), contextlib.redirect_stdout(output):
                self.assertEqual(module.main(factory), 0)
            self.assertIn('2 - Mover servo', output.getvalue())

    def test_group_menu_uses_each_position_and_enables_torque(self):
        for module in (cli, v3, v25):
            bus = self.bus()
            bus.read_servo.side_effect = lambda sid: driver.ServoState(sid, str(sid), {5: 120, 6: 150}[sid], 7.4, 0)
            bus.read_torque_enabled.return_value = False
            with patch('builtins.input', side_effect=['4', '5 6', '5', '3', '0']), patch.object(module.time, 'monotonic', side_effect=[0, 4]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(module.interactive_menu(bus, [5, 6]), 0)
            self.assertEqual(bus.move_verified.call_args_list, [call(5, 120, 0.5), call(6, 150, 0.5)])
            bus.move_group_direct.assert_called_once_with([(5, 125, 3), (6, 155, 3)])
            bus.move_many_verified.assert_not_called()
            self.assertEqual(bus.stop.call_args_list, [call(5), call(6)])

    def test_group_menu_requires_both_responses(self):
        bus = self.bus()
        bus.read_servo.side_effect = [driver.ServoState(5, '5', 120, 7.4, 0), TimeoutError('ID 6 sem resposta')]
        with patch('builtins.input', side_effect=['4', '', '', '', '0']), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.interactive_menu(bus, [5, 6]), 0)
        bus.move_many_verified.assert_not_called()
        bus.move_group_direct.assert_not_called()
        bus.move_verified.assert_not_called()

    def test_group_menu_rejects_duplicate_or_unknown_ids(self):
        for selection in ('5 5', '5 7', '5'):
            bus = self.bus()
            with patch('builtins.input', side_effect=['4', selection, '0']), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(cli.interactive_menu(bus, [5, 6]), 0)
            bus.move_many_verified.assert_not_called()
            bus.move_group_direct.assert_not_called()
            bus.move_verified.assert_not_called()

    def test_group_invalid_second_target_never_enables_first_torque(self):
        bus = self.bus()
        bus.read_torque_enabled.return_value = False
        bus.read_position_limits.return_value = (30, 210)
        states = [driver.ServoState(5, '5', 120, 7.4, 0), driver.ServoState(6, '6', 209, 7.4, 0)]
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(ValueError):
            cli.test_movement(bus, states, 5, 3, synchronized=True)
        bus.move_many_verified.assert_not_called()
        bus.move_verified.assert_not_called()

    def test_group_failed_prepare_stops_all(self):
        bus = self.bus()
        bus.move_many_verified.side_effect = ValueError('alvo nao confirmado')
        states = [driver.ServoState(5, '5', 120, 7.4, 0), driver.ServoState(6, '6', 150, 7.4, 0)]
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(ValueError):
            cli.test_movement(bus, states, 5, 3, synchronized=True)
        self.assertEqual(bus.stop.call_args_list, [call(5), call(6)])

    def test_direct_group_failure_stops_both(self):
        bus = self.bus()
        bus.move_group_direct.side_effect = ValueError('alvo direto nao confirmado')
        states = [driver.ServoState(5, '5', 120, 7.4, 0), driver.ServoState(6, '6', 150, 7.4, 0)]
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(ValueError):
            cli.test_movement(bus, states, -20, 3)
        self.assertEqual(bus.stop.call_args_list, [call(5), call(6)])
        bus.move_many_verified.assert_not_called()

    def test_cli_multiple_ids_defaults_to_direct_group(self):
        for module in (cli, v3, v25):
            bus = self.bus()
            bus.read_servo.side_effect = lambda sid: driver.ServoState(sid, str(sid), {5: 204.96, 6: 204.72}[sid], 7.4, 0)
            factory = MagicMock()
            factory.return_value.__enter__.return_value = bus
            with patch('sys.argv', ['servo.py', '--port', 'COM7', '--ids', '5', '6', '--move', '--delta', '-50', '--seconds', '3']), patch.object(module.time, 'monotonic', side_effect=[0, 4]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(module.main(factory), 0)
            bus.move_group_direct.assert_called_once_with([(5, 154.96, 3), (6, 154.72, 3)])
            bus.move_many_verified.assert_not_called()

    def test_voltage_collapse_stops_entire_group_immediately(self):
        for module in (cli, v3, v25):
            for voltage in (3.371, 8.5, float('nan')):
                bus = self.bus()
                states = [driver.ServoState(5, '5', 204.96, 7.4, 0), driver.ServoState(6, '6', 204.72, 7.4, 0)]
                bus.read_servo.return_value = driver.ServoState(5, '5', 203.52, voltage, 0)
                with patch.object(module.time, 'monotonic', return_value=0), contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, 'durante o movimento'):
                    module.test_movement(bus, states, -50, 2)
                bus.read_servo.assert_called_once_with(5)
                self.assertEqual(bus.stop.call_args_list, [call(5), call(6)])

    def test_voltage_check_also_applies_to_single_servo(self):
        bus = self.bus()
        state = bus.read_servo(6)
        bus.read_servo.return_value = driver.ServoState(6, '6', 149, 3.315, 0)
        with patch.object(cli.time, 'monotonic', return_value=0), contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, '3.315 V'):
            cli.test_movement(bus, [state], -20, 3)
        bus.stop.assert_called_once_with(6)


if __name__ == '__main__':
    unittest.main()
