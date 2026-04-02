FROM ros:jazzy

ENV DEBIAN_FRONTEND=noninteractive

# Install Gazebo Harmonic + ROS-Gazebo bridge + tools
RUN apt-get update && apt-get install -y \
    gz-harmonic \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-xacro \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-teleop-twist-keyboard \
    ros-jazzy-tf2-ros \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /ros2_ws
COPY src/ src/

# Build
RUN . /opt/ros/jazzy/setup.sh && \
    colcon build --symlink-install && \
    echo ". /opt/ros/jazzy/setup.bash" >> /root/.bashrc && \
    echo ". /ros2_ws/install/setup.bash" >> /root/.bashrc

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
