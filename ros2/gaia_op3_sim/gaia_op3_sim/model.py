"""Add a training harness, controllers and ideal sensors to an upstream URDF.

No upstream meshes or dynamics are redistributed or overwritten.
This is an educational simulator adapter, not an LX-225 hardware driver.
"""
import xml.etree.ElementTree as ET

JOINTS = [
    'r_sho_pitch', 'l_sho_pitch', 'r_sho_roll', 'l_sho_roll',
    'r_el', 'l_el', 'r_hip_yaw', 'l_hip_yaw', 'r_hip_roll', 'l_hip_roll',
    'r_hip_pitch', 'l_hip_pitch', 'r_knee', 'l_knee',
    'r_ank_pitch', 'l_ank_pitch', 'r_ank_roll', 'l_ank_roll',
    'head_pan', 'head_tilt',
]


def adapt_model(urdf, controllers_path, fixed_base=True):
    robot = ET.fromstring(urdf)
    names = {j.get('name') for j in robot.findall('joint')
             if j.get('type') != 'fixed'}
    if names != set(JOINTS):
        raise ValueError('The upstream joint set changed; review the OP3 adapter.')
    if robot.find('ros2_control') is not None:
        raise ValueError('The upstream model already has ros2_control; review it.')
    links = {link.get('name') for link in robot.findall('link')}
    if not {'base', 'body_link', 'head_tilt_link'} <= links:
        raise ValueError('The upstream link names changed.')

    if fixed_base:
        ET.SubElement(robot, 'link', name='world')
        joint = ET.SubElement(robot, 'joint', name='gaia_lab_support', type='fixed')
        ET.SubElement(joint, 'parent', link='world')
        ET.SubElement(joint, 'child', link='base')
        ET.SubElement(joint, 'origin', xyz='0 0 0.6', rpy='0 0 0')

    control = ET.SubElement(robot, 'ros2_control', name='GaiaOp3Lab', type='system')
    hardware = ET.SubElement(control, 'hardware')
    ET.SubElement(hardware, 'plugin').text = 'gz_ros2_control/GazeboSimSystem'
    for name in JOINTS:
        joint = ET.SubElement(control, 'joint', name=name)
        ET.SubElement(joint, 'command_interface', name='position')
        pos = ET.SubElement(joint, 'state_interface', name='position')
        ET.SubElement(pos, 'param', name='initial_value').text = '0.0'
        ET.SubElement(joint, 'state_interface', name='velocity')

    gazebo = ET.SubElement(robot, 'gazebo')
    plugin = ET.SubElement(gazebo, 'plugin',
                           filename='libgz_ros2_control-system.so',
                           name='gz_ros2_control::GazeboSimROS2ControlPlugin')
    ET.SubElement(plugin, 'parameters').text = str(controllers_path)

    imu = ET.fromstring("""
    <gazebo reference="body_link">
      <sensor name="gaia_lab_imu" type="imu">
        <always_on>true</always_on><update_rate>50</update_rate>
        <topic>/gaia/imu</topic><gz_frame_id>body_link</gz_frame_id>
      </sensor>
    </gazebo>""")
    robot.append(imu)
    # Camera sensor uses Gazebo's +X viewing convention. The optical frame
    # below uses ROS camera convention (+Z forward, +X right, +Y down).
    ET.SubElement(robot, 'link', name='gaia_camera_link')
    joint = ET.SubElement(robot, 'joint', name='gaia_camera_mount', type='fixed')
    ET.SubElement(joint, 'parent', link='head_tilt_link')
    ET.SubElement(joint, 'child', link='gaia_camera_link')
    ET.SubElement(joint, 'origin', xyz='0.04 0 0.04', rpy='0 0 0')
    ET.SubElement(robot, 'link', name='gaia_camera_optical_frame')
    joint = ET.SubElement(robot, 'joint', name='gaia_camera_optical', type='fixed')
    ET.SubElement(joint, 'parent', link='gaia_camera_link')
    ET.SubElement(joint, 'child', link='gaia_camera_optical_frame')
    ET.SubElement(joint, 'origin', xyz='0 0 0',
                  rpy='-1.5707963267948966 0 -1.5707963267948966')
    camera = ET.fromstring("""
    <gazebo reference="head_tilt_link">
      <sensor name="gaia_lab_camera" type="camera">
        <pose>0.04 0 0.04 0 0 0</pose>
        <always_on>true</always_on><update_rate>15</update_rate>
        <topic>/gaia/camera/image_raw</topic>
        <gz_frame_id>gaia_camera_optical_frame</gz_frame_id>
        <camera>
          <horizontal_fov>1.05</horizontal_fov>
          <image><width>320</width><height>240</height><format>R8G8B8</format></image>
          <clip><near>0.02</near><far>20</far></clip>
          <camera_info_topic>/gaia/camera/camera_info</camera_info_topic>
        </camera>
      </sensor>
    </gazebo>""")
    robot.append(camera)
    return ET.tostring(robot, encoding='unicode')
