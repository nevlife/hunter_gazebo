import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    gazebo_model_path = '/home/pgw/dev/gazebo_models_worlds_collection'
    hunter_base_share = get_package_share_directory('hunter_base')
    hunter_base_parent = os.path.dirname(hunter_base_share)
    combined_path = f'{gazebo_model_path}:{hunter_base_parent}:{hunter_base_share}/urdf'
    set_ign_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=combined_path
    )

    # RGL Gazebo Plugin paths
    rgl_plugin_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            get_package_share_directory('gazebo_fortress'))))),
        'external', 'RGLGazeboPlugin')
    set_ign_system_plugin_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_SYSTEM_PLUGIN_PATH',
        value=os.path.join(rgl_plugin_path, 'install', 'RGLServerPlugin')
    )
    set_ign_gui_plugin_path = SetEnvironmentVariable(
        name='IGN_GUI_PLUGIN_PATH',
        value=os.path.join(rgl_plugin_path, 'install', 'RGLVisualize')
    )
    set_rgl_patterns_dir = SetEnvironmentVariable(
        name='RGL_PATTERNS_DIR',
        value=os.path.join(rgl_plugin_path, 'lidar_patterns')
    )

    pkg_share = get_package_share_directory('gazebo_fortress')
    gazebo_world_path = os.path.join(pkg_share, 'world', 'simple_baylands.sdf')

    gazebo_simulator = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={'gz_args': f'-r {gazebo_world_path} -v 4'}.items()
    )

    car_sim_options = {
        'start_x': '2.0',
        'start_y': '0',
        'start_z': '0.5',
        'start_yaw': '0',
    }

    spawn_car = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('gazebo_fortress'),
                'launch', 'hunter_spawn.launch.py')
        ]),
        launch_arguments=car_sim_options.items()
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'use_sim_time': True}],
        remappings=[
            ('/gps', '/gps/raw'),
        ],
        arguments=[
            '/imu@sensor_msgs/msg/Imu@ignition.msgs.IMU',
            '/gps@sensor_msgs/msg/NavSatFix@ignition.msgs.NavSat',
            '/velodyne_points@sensor_msgs/msg/PointCloud2@ignition.msgs.PointCloudPacked',
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/joint_states@sensor_msgs/msg/JointState@ignition.msgs.Model',
            '/odometry/wheel@nav_msgs/msg/Odometry@ignition.msgs.Odometry',
            '/odometry/ground_truth@nav_msgs/msg/Odometry@ignition.msgs.Odometry',
            '/camera/raw@sensor_msgs/msg/Image[ignition.msgs.Image'
        ],
        output='screen'
    )

    static_tf_lidar = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_lidar',
        arguments=['0', '0', '0', '0', '0', '0', 'velodyne_sensor', 'hunter2/base_link/velodyne_sensor'],
        output='screen'
    )

    static_tf_imu = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_imu',
        arguments=['0', '0', '0.05', '0', '0', '0', 'base_link', 'hunter2/base_link/imu_sensor'],
        output='screen'
    )

    static_tf_gps = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_gps',
        arguments=['0', '0', '0.1', '0', '0', '0', 'base_link', 'hunter2/base_link/navsat_sensor'],
        output='screen'
    )

    static_tf_camera = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_camera',
        arguments=['0', '0', '0', '0', '0', '0', 'camera_link', 'hunter2/base_link/camera_sensor'],
        output='screen'
    )

    gps_covariance_relay = Node(
        package='gazebo_fortress',
        executable='gps_covariance_relay',
        name='gps_covariance_relay',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    vehicle_speed_publisher = Node(
        package='gazebo_fortress',
        executable='vehicle_speed_publisher',
        name='vehicle_speed_publisher',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        set_ign_resource_path,
        set_ign_system_plugin_path,
        set_ign_gui_plugin_path,
        set_rgl_patterns_dir,
        gazebo_simulator,
        spawn_car,
        bridge,
        static_tf_lidar,
        static_tf_imu,
        static_tf_gps,
        static_tf_camera,
        gps_covariance_relay,
        vehicle_speed_publisher,
    ])
