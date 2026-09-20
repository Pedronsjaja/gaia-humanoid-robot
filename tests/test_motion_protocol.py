import struct
import unittest

import servo_testbench as driver
import buslinker_v3 as v3
import buslinker_v2_5 as v25
from test_driver import FakeSerial


class MotionSerial(FakeSerial):
    def __init__(self, torque=False, confirm=True, enable=True):
        super().__init__()
        self.target = b''
        self.torque = torque
        self.confirm = confirm
        self.enable = enable

    def write(self, packet):
        self.packets.append(packet)
        sid, command = packet[2], packet[4]
        if command == 1:
            self.target = packet[5:-1]
        elif command == 31 and self.enable:
            self.torque = bool(packet[5])
        replies = {
            2: self.target if self.confirm else struct.pack('<HH', 670, 1000),
            21: struct.pack('<HH', 125, 875),
            30: b'\x00\x00\x00\x00',
            32: bytes([int(self.torque)]),
        }
        if command in replies:
            self.buffer.extend(driver.build_packet(sid, command, replies[command]))
        return len(packet)


class MotionProtocolTests(unittest.TestCase):
    def bus(self, cls, **kwargs):
        bus = cls.__new__(cls)
        bus.ser = MotionSerial(**kwargs)
        return bus

    def test_direct_target_confirmed_before_torque_enable(self):
        for cls in (driver.LX225Bus, v3.BusLinkerV3, v25.BusLinkerV2_5):
            for torque in (False, True):
                bus = self.bus(cls, torque=torque)
                bus.move_verified(6, 140.88, 3)
                expected = [1, 2, 32] if torque else [1, 2, 32, 31, 32]
                self.assertEqual([p[4] for p in bus.ser.packets], expected)
                self.assertEqual(bus.ser.target, struct.pack('<HH', 587, 3000))
                self.assertTrue(bus.ser.torque)

    def test_wrong_target_never_enables_torque(self):
        bus = self.bus(driver.LX225Bus, confirm=False)
        with self.assertRaises(ValueError):
            bus.move_verified(6, 140.88, 3)
        self.assertEqual([p[4] for p in bus.ser.packets], [1, 2])
        self.assertFalse(bus.ser.torque)

    def test_torque_enable_failure_is_reported(self):
        bus = self.bus(driver.LX225Bus, enable=False)
        with self.assertRaisesRegex(ValueError, 'torque continua desabilitado'):
            bus.move_verified(6, 140.88, 3)

    def test_configuration_queries_only_read(self):
        bus = self.bus(driver.LX225Bus)
        self.assertEqual(bus.read_position_limits(6), (30, 210))
        self.assertEqual(bus.read_mode(6), 0)
        self.assertFalse(bus.read_torque_enabled(6))
        self.assertEqual([p[4] for p in bus.ser.packets], [21, 30, 32])

    def test_group_confirms_every_target_before_one_broadcast(self):
        for cls in (driver.LX225Bus, v3.BusLinkerV3, v25.BusLinkerV2_5):
            bus = self.bus(cls)
            targets = [(5, 125.04, 3), (6, 155.04, 3)]
            # Emulate each servo retaining its individual prepared target.
            pending = {}
            def write(packet):
                bus.ser.packets.append(packet)
                sid, cmd = packet[2], packet[4]
                if cmd == 7:
                    pending[sid] = packet[5:-1]
                elif cmd == 8:
                    bus.ser.buffer.extend(driver.build_packet(sid, 8, pending[sid]))
                return len(packet)
            bus.ser.write = write
            bus.move_many_verified(targets)
            self.assertEqual([(p[2], p[4]) for p in bus.ser.packets], [(5, 7), (5, 8), (6, 7), (6, 8), (254, 11)])
            self.assertEqual(pending, {5: struct.pack('<HH', 521, 3000), 6: struct.pack('<HH', 646, 3000)})

    def test_group_unconfirmed_target_never_starts(self):
        for cls in (driver.LX225Bus, v3.BusLinkerV3, v25.BusLinkerV2_5):
            bus = self.bus(cls)
            def write(packet):
                bus.ser.packets.append(packet)
                if packet[4] == 8:
                    bus.ser.buffer.extend(driver.build_packet(packet[2], 8, b'\x00\x00\x00\x00'))
                return len(packet)
            bus.ser.write = write
            with self.assertRaisesRegex(ValueError, 'inicio nao enviado'):
                bus.move_many_verified([(5, 125, 3), (6, 155, 3)])
            self.assertNotIn(11, [p[4] for p in bus.ser.packets])

    def test_group_validates_whole_batch_before_write(self):
        for targets in ([(5, 125, 3), (5, 155, 3)], [(5, 125, 3), (6, 250, 3)]):
            bus = self.bus(driver.LX225Bus)
            with self.assertRaises(ValueError):
                bus.move_many_verified(targets)
            self.assertEqual(bus.ser.packets, [])

    def test_direct_group_sends_both_targets_before_any_read(self):
        for cls in (driver.LX225Bus, v3.BusLinkerV3, v25.BusLinkerV2_5):
            bus = self.bus(cls, torque=True)
            active = {}
            def write(packet):
                bus.ser.packets.append(packet)
                sid, cmd = packet[2], packet[4]
                if cmd == 1:
                    active[sid] = packet[5:-1]
                elif cmd == 2:
                    bus.ser.buffer.extend(driver.build_packet(sid, 2, active[sid]))
                elif cmd == 32:
                    bus.ser.buffer.extend(driver.build_packet(sid, 32, b'\x01'))
                return len(packet)
            bus.ser.write = write
            bus.move_group_direct([(5, 125.04, 3), (6, 155.04, 3)])
            self.assertEqual([(p[2], p[4]) for p in bus.ser.packets], [(5, 1), (6, 1), (5, 2), (5, 32), (6, 2), (6, 32)])
            self.assertEqual(active, {5: struct.pack('<HH', 521, 3000), 6: struct.pack('<HH', 646, 3000)})

    def test_direct_group_rejects_invalid_batch_before_writing(self):
        for targets in ([(5, 125, 3), (5, 155, 3)], [(5, 125, 3), (6, 250, 3)]):
            bus = self.bus(driver.LX225Bus)
            with self.assertRaises(ValueError):
                bus.move_group_direct(targets)
            self.assertEqual(bus.ser.packets, [])

    def test_direct_group_reports_wrong_target(self):
        bus = self.bus(driver.LX225Bus, confirm=False)
        with self.assertRaisesRegex(ValueError, 'alvo direto nao confirmado'):
            bus.move_group_direct([(5, 125, 3), (6, 155, 3)])
        self.assertEqual([p[4] for p in bus.ser.packets], [1, 1, 2])


if __name__ == '__main__':
    unittest.main()
