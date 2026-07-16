import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

FLEET_NAMES = ['alfa', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf',
               'hotel', 'india', 'juliett', 'kilo', 'lima', 'mike', 'november',
               'oscar', 'papa', 'quebec', 'romeo', 'sierra', 'tango', 'uniform',
               'victor', 'whiskey', 'xray', 'yankee', 'zulu']

def generate_fleet_nodes(context, *args, **kwargs):
    """
    OpaqueFunction que tem acesso ao 'context', que é o que o user escreveu
    em tempo real no terminal
    """

    # obtem o numero de barcos a serem instanciados
    num_boats_str = LaunchConfiguration('num_boats').perform(context)
    num_boats = int(num_boats_str)
    num_boats = min(num_boats, len(FLEET_NAMES))

    # obtem as coordenadas de spawn de cada barco no formato: x1,y1; x2,y2; ....
    positions_str = LaunchConfiguration('positions').perform(context)

    # obtem o mundo (.sdf) que se quer gerar
    world_name = LaunchConfiguration('world_name').perform(context)

    world_offsets = {
        'ocean': (0.0, 0.0),
        'sydney_regatta': (-500.0, 188.0)
    }

    offset_x, offset_y = world_offsets.get(world_name, (0.0, 0.0))

    positions_list = []
    if positions_str:
        ordered_pairs = positions_str.split(';')

        for ord_pair in ordered_pairs:

            if ',' in ord_pair:
                x, y = ord_pair.split(',')
                real_x = float(x.strip()) + offset_x
                real_y = float(y.strip()) + offset_y
                positions_list.append((real_x, real_y))

    nodes_to_init = []

    pkg_sprint_sbr = get_package_share_directory('sprint_sbr')
    boat_spawn_path = os.path.join(pkg_sprint_sbr, 'launch', 'boat_spawn.launch.py')
    custom_sensors_path = os.path.join(pkg_sprint_sbr, 'config', 'sensors.yaml')

    for i in range(num_boats):

        boat_name = FLEET_NAMES[i]
        
        if i < len(positions_list):
            pos_x, pos_y = positions_list[i]
        else:
            pos_x = (float(i * 10)) + offset_x
            pos_y = 0.0 + offset_y

        spawn_cmd = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(boat_spawn_path),
            launch_arguments={
                'namespace': boat_name,
                'x': str(pos_x),
                'y': str(pos_y),
                'z': '1.0',
                'yaw': '0.0',
                'sensor_yaml': custom_sensors_path,
                'world_name': world_name
            }.items(),
        )
        nodes_to_init.append(spawn_cmd)

        perception_node = Node(
            package='sprint_sbr',
            executable='perception_node.py',
            name=f'perception_{boat_name}',
            parameters=[{
                'boat_name': boat_name,
                'use_sim_time': True
            }],            
            output='screen'
        )
        nodes_to_init.append(perception_node)

        localization_config = os.path.join(pkg_sprint_sbr, 'config', 'localization.yaml')

        ekf_node = Node(
            package='robot_localization',
            executable='ekf_node',
            name=f'ekf_filter',
            namespace=boat_name,
            parameters=[localization_config, {
                'use_sim_time': True,
                'map_frame': 'map',
                'odom_frame': f'{boat_name}/odom',
                'base_link_frame': f'{boat_name}/base_link',
                'world_frame': f'{boat_name}/odom'
            }],
            remappings=[
                ('imu', 'sensors/imu/data')
            ],
            output='screen'
        )
        nodes_to_init.append(ekf_node)

        navsat_node = Node(
            package='robot_localization',
            executable='navsat_transform_node',
            name='navsat_transform',
            namespace=boat_name,
            parameters=[localization_config, {
                'use_sim_time' : True
            }],
            remappings=[
                ('gps/fix', 'sensors/gps/fix'),
                ('imu', 'sensors/imu/data')     
            ],
            output='screen'
        )
        nodes_to_init.append(navsat_node)

    return nodes_to_init

def generate_launch_description():

    return LaunchDescription([

        DeclareLaunchArgument(
            'num_boats',
            default_value='1',
            description='numero de barcos autônomos para instanciar (max 7)'
        ),

        DeclareLaunchArgument(
            'positions',
            default_value='0,0',
            description='posicoes no formato "x,y; x,y"'
        ),

        DeclareLaunchArgument(
            'world_name',
            default_value='ocean',
            description='nome do arquivo .sdf'
        ),

        OpaqueFunction(function=generate_fleet_nodes)
    ])