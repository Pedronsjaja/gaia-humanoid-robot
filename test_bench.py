import argparse
import csv
import math
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import bench_tools as b
import servo_testbench as d
from test_driver import FakeSerial


class ServoSerial(FakeSerial):
    def __init__(self):
        super().__init__()
        self.ids = {1}
        self.offset = 0

    def write(self, packet):
        self.packets.append(packet)
        sid, command = packet[2], packet[4]
        if sid not in self.ids:
            return len(packet)
        params = packet[5:-1]
        reply = {14: bytes([sid]), 19: struct.pack('<b', self.offset),
                 26: bytes([35]), 27: struct.pack('<H', 7400), 28: struct.pack('<h', 500)}
        if command == 13:
            self.ids.remove(sid)
            self.ids.add(params[0])
        elif command == 17:
            self.offset = struct.unpack('<b', params)[0]
        elif command in reply:
            self.buffer.extend(d.build_packet(sid, command, reply[command]))
        return len(packet)


class BenchTests(unittest.TestCase):
    def bus(self):
        bus = d.LX225Bus.__new__(d.LX225Bus)
        bus.ser = ServoSerial()
        bus._last_angle = {}
        return bus

    def test_temperature_and_velocity(self):
        bus = self.bus()
        first = bus.read_servo(1)
        second = bus.read_servo(1)
        self.assertEqual(first.temperature_c, 35)
        self.assertEqual(first.voltage_v, 7.4)
        self.assertTrue(math.isnan(first.velocity_dps))
        self.assertEqual(second.velocity_dps, 0)

    def test_id_change_and_collision(self):
        bus = self.bus()
        with patch.object(d, 'READ_TIMEOUT_S', 0.002), patch.object(d.time, 'sleep'):
            bus.write_id(1, 2)
            self.assertEqual(bus.read_id(2), 2)
            bus.ser.ids.add(3)
            with self.assertRaises(ValueError):
                bus.write_id(2, 3)
        self.assertEqual(bus.ser.ids, {2, 3})

    def test_signed_offset_save(self):
        bus = self.bus()
        with patch.object(d.time, 'sleep'):
            bus.set_offset(1, -12, save=True)
        self.assertEqual(bus.read_offset(1), -12)
        self.assertIn(18, [p[4] for p in bus.ser.packets])
        for ticks in (-126, 126, 0.5):
            with self.assertRaises(ValueError):
                bus.set_offset(1, ticks)

    def test_offset_failure_does_not_save(self):
        bus = self.bus()
        with patch.object(bus, 'read_offset', return_value=0), patch.object(d.time, 'sleep'):
            with self.assertRaises(ValueError):
                bus.set_offset(1, 12, save=True)
        self.assertNotIn(18, [p[4] for p in bus.ser.packets])

    def test_registry_and_graph_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'servos.json'
            b.save_registry(path, {'1': 'joelho'})
            self.assertEqual(b.load_registry(path), {'1': 'joelho'})
            rec = b.Recorder(tmp)
            b.sample(self.bus(), [1], {'1': 'joelho'}, rec)
            rec.failure(2, TimeoutError('Sem resposta'))
            rec.close()
            self.assertGreater((rec.folder / 'graficos.png').stat().st_size, 1000)
            with (rec.folder / 'telemetria.csv').open(encoding='utf-8') as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(rows[0]['temperature_c'], '35.0')
            self.assertEqual(rows[1]['status'], 'Sem resposta')

    def test_calibration_report_and_stop_on_failure(self):
        args = argparse.Namespace(max_temp=60, deltas=[0], seconds=0, settle=0,
                                  samples=2, interval=0, tolerance=2)
        with tempfile.TemporaryDirectory() as tmp:
            bus = self.bus()
            rec = b.Recorder(tmp)
            self.assertEqual(b.calibrate(bus, args, [1], {}, rec), 0)
            self.assertTrue((rec.folder / 'calibracao.csv').exists())
            self.assertEqual(bus.ser.packets[-1][4], 12)
            rec.close()
            rec = b.Recorder(tmp)
            original = bus.read_servo
            count = [0]
            def fail_after_move(*a, **kw):
                count[0] += 1
                if count[0] > 1:
                    raise TimeoutError('desconectado')
                return original(*a, **kw)
            with patch.object(bus, 'read_servo', side_effect=fail_after_move):
                with self.assertRaises(TimeoutError):
                    b.calibrate(bus, args, [1], {}, rec)
            self.assertEqual(bus.ser.packets[-1][4], 12)
            rec.close()


if __name__ == '__main__':
    unittest.main()
