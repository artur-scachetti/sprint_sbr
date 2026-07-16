import os
import yaml
import io
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue

from vrx_gz.model import Model

def launch_setup(context, *args, **kwargs):
    ns = LaunchConfiguration('namespace').perform(context)
    yaml_path = LaunchConfiguration('sensor_yaml').perform(context)
    world = LaunchConfiguration('world_name').perform(context)
    x = LaunchConfiguration('x').perform(context)
    y = LaunchConfiguration('y').perform(context)
    yaw = LaunchConfiguration('yaw').perform(context)

    with open(yaml_path, 'r') as f:
        user_sensors = yaml.safe_load(f)

    if user_sensors is None:
        user_sensors = []
    elif isinstance(user_sensors, dict):
        user_sensors = [user_sensors]

    vrx_config = [{
        'model_name': ns,
        'model_type': 'wam-v',
        'sensors': user_sensors
    }]
    
    yaml_stream = io.StringIO(yaml.dump(vrx_config))
    models = Model.FromConfig(yaml_stream)
    model = models[0]

    spawn_arguments = model.spawn_args()
    spawn_arguments.extend(['-x', x, '-y', y, '-z', '1.0', '-Y', yaw])

    spawn_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=spawn_arguments, 
        output='screen'
    )

    wamv_xacro = os.path.join(
        get_package_share_directory('wamv_gazebo'), 
        'urdf', 
        'wamv_gazebo.urdf.xacro'
    )
    
    robot_desc_cmd = f"xacro {wamv_xacro}"
    robot_description = ParameterValue(Command([robot_desc_cmd]), value_type=str)
    
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=ns,
        parameters=[{
            'robot_description': robot_description, 
            'use_sim_time': True, 
            'frame_prefix': f"{ns}/" 
        }],
        remappings=[('/joint_states', f'/{ns}/joint_states')],
        output='screen'
    )
    
    tf_broadcaster = Node(
        package='vrx_ros',
        executable='pose_tf_broadcaster',
        namespace=ns,
        output='screen'
    )

    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        namespace=ns,
        arguments=[
            f'/world/{world}/model/{ns}/link/{ns}/imu_wamv_link/sensor/imu_wamv_sensor/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            f'/world/{world}/model/{ns}/link/{ns}/gps_wamv_link/sensor/navsat/navsat@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat'
        ],
        remappings=[
            (f'/world/{world}/model/{ns}/link/{ns}/imu_wamv_link/sensor/imu_wamv_sensor/imu', f'/{ns}/sensors/imu/data'),
            (f'/world/{world}/model/{ns}/link/{ns}/gps_wamv_link/sensor/navsat/navsat', f'/{ns}/sensors/gps/fix')
        ],
        output='screen'
    )

    return [spawn_node, rsp_node, tf_broadcaster, bridge_node]

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('world_name', default_value='ocean', description='nome do mundo'),
        DeclareLaunchArgument('namespace', default_value='alfa', description='nome do barco'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('z', default_value='1.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
        DeclareLaunchArgument('sensor_yaml', description='caminho absoluto para o sensors.yaml'),
        OpaqueFunction(function=launch_setup)
    ])