import struct
import unittest
from unittest.mock import patch

import servo_testbench as d
from buslinker_v3 import BusLinkerV3


class FakeSerial:
    def __init__(self, reply=b''):
        self.reply = reply
        self.buffer = bytearray()
        self.packets = []

    def reset_input_buffer(self):
        self.buffer.clear()

    def write(self, packet):
        self.packets.append(packet)
        self.buffer.extend(self.reply)
        return len(packet)

    def flush(self):
        pass

    @property
    def in_waiting(self):
        return min(1, len(self.buffer))  # Resposta fragmentada em bytes.

    def read(self, count):
        data = bytes(self.buffer[:count])
        del self.buffer[:count]
        return data


class DriverTests(unittest.TestCase):
    def bus(self, reply=b''):
        bus = BusLinkerV3.__new__(BusLinkerV3)
        bus.ser = FakeSerial(reply)
        bus._last_angle = {}
        return bus

    def test_known_packet(self):
        self.assertEqual(d.build_packet(1, 1, struct.pack('<HH', 500, 1000)),
                         bytes.fromhex('55 55 01 07 01 f4 01 e8 03 16'))

    def test_fragmented_echo_and_response(self):
        reply = d.build_packet(1, 28) + d.build_packet(1, 28, b'\xf4\x01')
        self.assertEqual(self.bus(reply).read_angle_deg(1), 120)

    def test_invalid_replies(self):
        good = d.build_packet(1, 28, b'\xf4\x01')
        for reply in (d.build_packet(1, 28) + b'\xf4\x01', good[:-1],
                      good[:-1] + bytes([good[-1] ^ 1]),
                      d.build_packet(2, 28, b'\xf4\x01'),
                      d.build_packet(1, 27, b'\xf4\x01')):
            with self.subTest(reply=reply), patch.object(d, 'READ_TIMEOUT_S', 0.005):
                with self.assertRaises(TimeoutError):
                    self.bus(reply).read_angle_deg(1)

    def test_invalid_inputs_never_write(self):
        bus = self.bus()
        for angle, duration in ((float('nan'), 1), (float('inf'), 1),
                                (300, 1), (-1, 1), (120, -1),
                                (120, float('nan')), (120, 31)):
            for method in (bus.move, bus.prepare_move):
                with self.assertRaises(ValueError):
                    method(1, angle, duration)
        self.assertEqual(bus.ser.packets, [])

    def test_batch_validated_before_write(self):
        for targets in ([(1, 120, 1), (2, 120, -1)],
                        [(1, 120, 1), (1, 130, 1)]):
            bus = self.bus()
            with self.assertRaises(ValueError):
                bus.move_many(targets)
            self.assertEqual(bus.ser.packets, [])

    def test_three_servos_start(self):
        for sync in (False, True):
            bus = self.bus()
            bus.move_many([(1, 120, 1), (2, 120, 1), (3, 120, 1)], synchronized=sync)
            expected = [(1, 7), (2, 7), (3, 7)]
            expected += [(254, 11)] if sync else [(1, 11), (2, 11), (3, 11)]
            self.assertEqual([(p[2], p[4]) for p in bus.ser.packets], expected)

    def test_speed_and_limits(self):
        bus = self.bus()
        bus.read_angle_deg = lambda sid: 120
        bus.move_at_speed(1, 180, 60)
        self.assertEqual(struct.unpack('<HH', bus.ser.packets[-1][5:-1]), (750, 1000))
        for angle, speed in ((300, 60), (180, 0), (180, float('nan')), (180, 0.1)):
            with self.assertRaises(ValueError):
                bus.move_at_speed(1, angle, speed)

    def test_broadcast_read_rejected(self):
        with self.assertRaises(ValueError):
            self.bus().read_angle_deg(254)


if __name__ == '__main__':
    unittest.main()
