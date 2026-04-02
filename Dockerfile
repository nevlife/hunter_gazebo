FROM ros:humble

ENV DEBIAN_FRONTEND=noninteractive

# Install Gazebo Fortress + ROS-Gazebo bridge + tools
RUN apt-get update && apt-get install -y \
    ignition-fortress \
    ros-humble-ros-gz-sim \
    ros-humble-ros-gz-bridge \
    ros-humble-xacro \
    ros-humble-robot-state-publisher \
    ros-humble-teleop-twist-keyboard \
    ros-humble-tf2-ros \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /ros2_ws
COPY src/ src/

# Build RGL Plugin (optional, requires NVIDIA)
# RUN cd /ros2_ws/external/RGLGazeboPlugin && \
#     mkdir build && cd build && \
#     cmake .. -DCMAKE_INSTALL_PREFIX=../install && \
#     make -j$(nproc) && make install

# Build
RUN . /opt/ros/humble/setup.sh && \
    colcon build --symlink-install && \
    echo ". /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo ". /ros2_ws/install/setup.bash" >> /root/.bashrc

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
