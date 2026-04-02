import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    # Set Gazebo model path
    gazebo_model_path = '/home/pgw/dev/gazebo_models_worlds_collection'
    hunter_base_share = get_package_share_directory('hunter_base')
    hunter_base_parent = os.path.dirname(hunter_base_share)
    combined_path = f'{gazebo_model_path}:{hunter_base_parent}:{hunter_base_share}/urdf'
    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=combined_path
    )

    pkg_share = get_package_share_directory('gazebo_jetty')
    gazebo_world_path = os.path.join(pkg_share, 'world', 'empty_with_gps.sdf')

    gazebo_simulator = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={'gz_args': f'-r {gazebo_world_path} -v 4'}.items()
    )

    car_sim_options = {
        'start_x': '0',
        'start_y': '0',
        'start_z': '0.4',
        'start_yaw': '0',
    }

    spawn_car = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('gazebo_jetty'),
                'launch', 'hunter_spawn.launch.py')
        ]),
        launch_arguments=car_sim_options.items()
    )

    # Bridge between Gazebo Harmonic and ROS 2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'use_sim_time': True}],
        remappings=[
            ('/velodyne_points/points', '/velodyne_points'),
            ('/gps', '/gps/raw'),
        ],
        arguments=[
            '/imu@sensor_msgs/msg/Imu@gz.msgs.IMU',
            '/gps@sensor_msgs/msg/NavSatFix@gz.msgs.NavSat',
            '/velodyne_points/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/odometry/ground_truth@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/camera/raw@sensor_msgs/msg/Image[gz.msgs.Image'
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
        package='gazebo_jetty',
        executable='gps_covariance_relay',
        name='gps_covariance_relay',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    vehicle_speed_publisher = Node(
        package='gazebo_jetty',
        executable='vehicle_speed_publisher',
        name='vehicle_speed_publisher',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        set_gz_resource_path,
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
