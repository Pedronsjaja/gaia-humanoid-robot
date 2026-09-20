"""Launch the OP3 teaching lab (ROS 2 Jazzy / Gazebo Harmonic)."""
import os
from pathlib import Path
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            OpaqueFunction, SetEnvironmentVariable)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from gaia_op3_sim.model import adapt_model


def launch_setup(context):
    share = Path(get_package_share_directory('gaia_op3_sim'))
    description = Path(get_package_share_directory('op3_description'))
    gui = LaunchConfiguration('gui').perform(context) == 'true'
    fixed = LaunchConfiguration('fixed_base').perform(context) == 'true'
    doc = xacro.process_file(str(description / 'urdf/robotis_op3.urdf.xacro'))
    model = adapt_model(doc.toxml(), share / 'config/controllers.yaml', fixed)
    resource_path = str(description.parent)
    previous = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    if previous:
        resource_path += os.pathsep + previous
    gz_args = '-r -v 3 ' + ('' if gui else '-s --headless-rendering ')
    gz_args += str(share / 'worlds/lab.sdf')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(
            Path(get_package_share_directory('ros_gz_sim')) / 'launch/gz_sim.launch.py')),
        launch_arguments={'gz_args': gz_args, 'on_exit_shutdown': 'true'}.items())
    state = Node(package='robot_state_publisher', executable='robot_state_publisher',
                 parameters=[{'robot_description': ParameterValue(model, value_type=str), 'use_sim_time': True}])
    spawn = Node(package='ros_gz_sim', executable='create',
                 arguments=['-world', 'gaia_lab', '-topic', '/robot_description',
                            '-name', 'gaia_op3_lab', '-z', '0' if fixed else '0.285'],
                 output='screen')
    # Spawners wait for the controller manager instead of assuming a fixed delay.
    controllers = [
        Node(package='controller_manager', executable='spawner',
             arguments=[name, '--controller-manager-timeout', '120'],
             output='screen')
        for name in ['joint_state_broadcaster', 'joint_trajectory_controller']
    ]
    bridge = Node(package='ros_gz_bridge', executable='parameter_bridge',
                  parameters=[{'config_file': str(share / 'config/bridge.yaml'),
                               'use_sim_time': True}], output='screen')
    return [SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', resource_path),
            gazebo, state, spawn, bridge, *controllers]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true', choices=['true', 'false']),
        DeclareLaunchArgument('fixed_base', default_value='true', choices=['true', 'false']),
        OpaqueFunction(function=launch_setup),
    ])
