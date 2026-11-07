# Humanoid Robotic Systems

Coursework for [Humanoid Robotic Systems](https://www.moodle.tum.de/course/info.php?id=123131&lang=en) at TUM, winter semester 2026/27.

Tutorial 1 covers Python packages, ROS 2 publishers/subscribers and services,
and colour-based object detection with OpenCV.

Ubuntu 24.04, ROS 2 Jazzy. Build the workspace with:

```bash
source /opt/ros/jazzy/setup.bash
cd tutorial_ws
colcon build --symlink-install
source install/setup.bash
```

The camera bag used for the vision exercise is course material and is not included.
