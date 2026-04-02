FROM ros:kilted

ENV DEBIAN_FRONTEND=noninteractive

# Install Gazebo Jetty + ROS-Gazebo bridge + tools
RUN apt-get update && apt-get install -y \
    gz-jetty \
    ros-kilted-ros-gz-sim \
    ros-kilted-ros-gz-bridge \
    ros-kilted-xacro \
    ros-kilted-robot-state-publisher \
    ros-kilted-teleop-twist-keyboard \
    ros-kilted-tf2-ros \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /ros2_ws
COPY src/ src/

# Build
RUN . /opt/ros/kilted/setup.sh && \
    colcon build --symlink-install && \
    echo ". /opt/ros/kilted/setup.bash" >> /root/.bashrc && \
    echo ". /ros2_ws/install/setup.bash" >> /root/.bashrc

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
