"""Run only against the Gaia OP3 simulator, never against physical hardware."""
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import JointState, Image, CameraInfo, Imu
from rosgraph_msgs.msg import Clock
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from controller_manager_msgs.srv import ListControllers


def main():
    rclpy.init()
    node = Node('gaia_sim_smoke')
    received = {}
    subscriptions = []
    for name, kind, topic in [
        ('joints', JointState, '/joint_states'),
        ('image', Image, '/gaia/camera/image_raw'),
        ('camera_info', CameraInfo, '/gaia/camera/camera_info'),
        ('imu', Imu, '/gaia/imu'),
        ('clock', Clock, '/clock'),
    ]:
        subscriptions.append(node.create_subscription(
            kind, topic, lambda msg, key=name: received.__setitem__(key, msg),
            qos_profile_sensor_data))
    publisher = node.create_publisher(
        JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)

    def wait_until(predicate, timeout, description):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
            if predicate():
                print('PASS:', description, flush=True)
                return
        raise RuntimeError(description + '; head_pan=' + str(joint_position())
                           + '; received: ' + ', '.join(received))

    def joint_position():
        msg = received.get('joints')
        if msg is None or 'head_pan' not in msg.name:
            return float('inf')
        return msg.position[msg.name.index('head_pan')]

    try:
        wait_until(lambda: len(received) == 5, 150, 'clock, joints, camera, CameraInfo and IMU')
        assert len(received['joints'].name) == 20
        assert received['image'].width == 320 and len(received['image'].data) > 0
        assert received['image'].header.frame_id == 'gaia_camera_optical_frame'
        assert received['camera_info'].width == 320
        assert received['imu'].header.frame_id == 'body_link'
        client = node.create_client(ListControllers, '/controller_manager/list_controllers')
        wait_until(client.service_is_ready, 30, 'controller manager service')
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            future = client.call_async(ListControllers.Request())
            wait_until(future.done, 15, 'controller state response')
            states = {c.name: c.state for c in future.result().controller}
            if states.get('joint_trajectory_controller') == 'active':
                break
            rclpy.spin_once(node, timeout_sec=0.5)
        else:
            raise RuntimeError('trajectory controller did not become active')
        wait_until(lambda: publisher.get_subscription_count() > 0, 30, 'active trajectory subscriber')
        for target in (0.15, 0.0):
            msg = JointTrajectory()
            msg.joint_names = ['head_pan']
            point = JointTrajectoryPoint()
            point.positions = [target]
            point.time_from_start.sec = 2
            msg.points = [point]
            publisher.publish(msg)
            wait_until(lambda: abs(joint_position() - target) < 0.025,
                       40, f'head_pan reaches {target} rad')
        print('Simulation smoke test passed; not a balance or visual-quality test.', flush=True)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
