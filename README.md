# Hunter Gazebo Harmonic Simulation

Gazebo Harmonic(gz-sim 8) 환경에서 동작하는 Hunter 로봇 시뮬레이션 패키지입니다. Ackermann Steering 구조를 지원하며, Gazebo Harmonic native 플러그인(`gz-sim-*`)을 사용합니다.

## 패키지 구성

| 패키지 | 설명 |
|---|---|
| `gazebo_harmonic` | 시뮬레이션 환경, Launch 파일, URDF/SDF, 컨트롤러 설정 |
| `hunter_base` | Hunter 로봇 기본 URDF 모델 및 메쉬 리소스 |

## 시스템 구성

### 조향 시스템

Hunter 로봇은 **Ackermann Steering** 구조를 기반으로 합니다.

- **구동 방식**: 후륜 구동(RWD), 전륜 조향
- **플러그인**: `gz-sim-ackermann-steering-system`
- **속도 제한**: ±10 m/s
- **가속도 제한**: ±5 m/s²
- **조향 제한**: ±0.461 rad

### 센서

| 센서 | 모델 | 토픽 | 주파수 | 노이즈 |
|---|---|---|---|---|
| LiDAR | Velodyne VLP-32C | `/velodyne_points` | 10 Hz | Gaussian stddev 0.008 m |
| IMU | Generic IMU | `/imu` | 100 Hz | Gaussian (각속도/선가속도별 상이) |
| GPS | Generic NavSat | `/gps/fix` | 10 Hz | Gaussian stddev 0.00000045 deg |

> **GPS 파이프라인**: Gazebo 내부 토픽 `/gps` → 브리지 → `/gps/raw` → `gps_covariance_relay` 노드 → `/gps/fix`
> `gps_covariance_relay` 노드는 공분산(covariance) 정보를 추가하여 표준 `NavSatFix` 포맷으로 변환합니다.

### IMU 노이즈 파라미터

| 축 | 각속도 stddev (rad/s) | 선가속도 stddev (m/s²) |
|---|---|---|
| X | 0.012432 | 0.264649 |
| Y | 0.013663 | 0.406186 |
| Z | 0.211278 | 0.153983 |

### 오도메트리

| 토픽 | 설명 |
|---|---|
| `/odom` | Ackermann 플러그인 기반 오도메트리 (`odom` → `base_link`) |
| `/odometry/ground_truth` | 물리 엔진 기반 ground truth (`world` → `base_link`) |
| `/joint_states` | 모든 조인트 상태 (50 Hz) |

## ROS-Gazebo 브리지 토픽

| Gazebo 토픽 | ROS 토픽 | 메시지 타입 |
|---|---|---|
| `/imu` | `/imu` | `sensor_msgs/Imu` |
| `/gps` | `/gps/raw` | `sensor_msgs/NavSatFix` |
| `/velodyne_points/points` | `/velodyne_points` | `sensor_msgs/PointCloud2` |
| `/cmd_vel` | `/cmd_vel` | `geometry_msgs/Twist` |
| `/clock` | `/clock` | `rosgraph_msgs/Clock` |
| `/odom` | `/odom` | `nav_msgs/Odometry` |
| `/odometry/ground_truth` | `/odometry/ground_truth` | `nav_msgs/Odometry` |
| `/joint_states` | `/joint_states` | `sensor_msgs/JointState` |

## 의존성

```bash
sudo apt install \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-teleop-twist-keyboard
```

## 빌드

```bash
cd ~/dev/gazebo_harmonic
colcon build
source install/setup.bash
```

## 실행

### Empty World (GPS 포함)

```bash
ros2 launch gazebo_harmonic hunter_sim_start.launch.py
```

### Baylands World

```bash
ros2 launch gazebo_harmonic hunter_simple_baylands.launch.py
```

### 키보드 원격 제어

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## 월드 파일

| 파일 | 설명 |
|---|---|
| `empty_with_gps.sdf` | 빈 평지 + GPS용 구면 좌표계 설정 (기본) |
| `simple_baylands.sdf` | Baylands 지형 환경 |

### GPS 기준 좌표 (empty_with_gps)

- 위도: 37.2397°N
- 경도: 126.7736°E

## 플러그인 (Gazebo Harmonic)

| 플러그인 파일명 | 역할 |
|---|---|
| `gz-sim-ackermann-steering-system` | 조향 + 구동 제어, `/odom` 발행 |
| `gz-sim-joint-state-publisher-system` | `/joint_states` 발행 |
| `gz-sim-odometry-publisher-system` | ground truth 오도메트리 발행 |
| `gz-sim-imu-system` | IMU 센서 처리 |
| `gz-sim-navsat-system` | GPS 센서 처리 |
