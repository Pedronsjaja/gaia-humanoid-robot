"""Regression checks against the actual pinned ROBOTIS description."""
import os
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
import xacro
import xacro.substitution_args
import yaml
from gaia_op3_sim.model import adapt_model, JOINTS


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        override = os.environ.get('OP3_DESCRIPTION_PATH')
        if override:
            cls.description = Path(override)
            xacro.substitution_args._eval_find = lambda name: str(cls.description.parent / name)
        else:
            from ament_index_python.packages import get_package_share_directory
            cls.description = Path(get_package_share_directory('op3_description'))
        cls.urdf = xacro.process_file(str(cls.description / 'urdf/robotis_op3.urdf.xacro')).toxml()
        cls.original = ET.fromstring(cls.urdf)

    def test_preserves_original_geometry_dynamics_and_limits(self):
        adapted = ET.fromstring(adapt_model(self.urdf, '/tmp/controllers.yaml'))
        for kind in ('link', 'joint'):
            for element in self.original.findall(kind):
                match = adapted.find(f"{kind}[@name='{element.get('name')}']")
                self.assertEqual(ET.tostring(element), ET.tostring(match))

    def test_fixed_support_and_free_base_are_distinct(self):
        fixed = ET.fromstring(adapt_model(self.urdf, '/tmp/c.yaml'))
        free = ET.fromstring(adapt_model(self.urdf, '/tmp/c.yaml', False))
        self.assertEqual(fixed.find("joint[@name='gaia_lab_support']/parent").get('link'), 'world')
        self.assertIsNone(free.find("link[@name='world']"))
        self.assertIsNone(free.find("joint[@name='gaia_lab_support']"))

    def test_controller_configuration_matches_all_actual_joints(self):
        config = yaml.safe_load((Path(__file__).parents[1] / 'config/controllers.yaml').read_text())
        joints = config['joint_trajectory_controller']['ros__parameters']['joints']
        self.assertEqual(set(joints), set(JOINTS))
        self.assertEqual(len(joints), 20)
        robot = ET.fromstring(adapt_model(self.urdf, '/tmp/c.yaml'))
        self.assertEqual({j.get('name') for j in robot.findall('ros2_control/joint')}, set(joints))
        for j in robot.findall('ros2_control/joint'):
            self.assertEqual([i.get('name') for i in j.findall('command_interface')], ['position'])

    def test_changed_upstream_and_duplicate_adapter_fail(self):
        changed = ET.fromstring(self.urdf)
        changed.find("joint[@name='head_pan']").set('name', 'unexpected')
        with self.assertRaises(ValueError):
            adapt_model(ET.tostring(changed), '/tmp/c.yaml')
        with self.assertRaises(ValueError):
            adapt_model(adapt_model(self.urdf, '/tmp/c.yaml'), '/tmp/c.yaml')

    def test_sensors_have_frames_and_bridge_topics(self):
        robot = ET.fromstring(adapt_model(self.urdf, '/tmp/c.yaml'))
        config = yaml.safe_load((Path(__file__).parents[1] / 'config/bridge.yaml').read_text())
        topics = {item['gz_topic_name'] for item in config}
        links = {link.get('name') for link in robot.findall('link')}
        sensors = robot.findall('gazebo/sensor')
        self.assertEqual({s.get('type') for s in sensors}, {'imu', 'camera'})
        for sensor in sensors:
            self.assertIn(sensor.findtext('topic'), topics)
            self.assertIn(sensor.findtext('gz_frame_id'), links)


if __name__ == '__main__':
    unittest.main()
