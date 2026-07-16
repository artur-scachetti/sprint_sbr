import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable, DeclareLaunchArgument, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, SetParameter

def launch_setup(context, *args, **kwargs):
    
    num_boats_arg = LaunchConfiguration('num_boats').perform(context)
    positions_arg = LaunchConfiguration('positions').perform(context)
    world_name = LaunchConfiguration('world_name').perform(context)

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_sprint_sbr = get_package_share_directory('sprint_sbr')

    world_path = os.path.join(pkg_sprint_sbr, 'world', f'{world_name}.sdf')
    
    gz_sim_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_path}'}.items(),
    )

    fleet_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_sprint_sbr, 'launch', 'fleet.launch.py')
        ),
        launch_arguments={
            'num_boats': num_boats_arg,
            'positions': positions_arg,
            'world_name': world_name
        }.items()
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='global_clock_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return [gz_sim_cmd, fleet_launch, clock_bridge]


def generate_launch_description():
    pkg_sprint_sbr = get_package_share_directory('sprint_sbr')
    pkg_wamv_desc = get_package_share_directory('wamv_description')
    pkg_wamv_gazebo = get_package_share_directory('wamv_gazebo')

    sprint_sbr_share_parent = os.path.dirname(pkg_sprint_sbr)
    wamv_desc_share = os.path.dirname(pkg_wamv_desc)
    wamv_gazebo_share = os.path.dirname(pkg_wamv_gazebo)

    model_paths = f"{sprint_sbr_share_parent}:{wamv_desc_share}:{wamv_gazebo_share}"

    set_gz_path_cmd = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        model_paths
    )
    
    return LaunchDescription([
        SetParameter(name='use_sim_time', value=True),
        
        DeclareLaunchArgument('num_boats', default_value='1', description='quantidade de barcos'),
        DeclareLaunchArgument('positions', default_value='0,0', description='posições X,Y; x,y; ...'),
        DeclareLaunchArgument('world_name', default_value='ocean', description='nome do mundo (.sdf)'),
        
        set_gz_path_cmd,
        OpaqueFunction(function=launch_setup)
    ])