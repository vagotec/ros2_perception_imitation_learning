# Phase 04 – TF2 & Camera-to-Robot Calibration

## ROS 2 Perception & Imitation Learning

Phase 04 connects the 3D perception results from Phase 03 with a robot coordinate system.

In Phase 03, the ZED 2 provided spatial information in the camera coordinate frame:

```text
PointCloud2
    ↓
3D Point
    ↓
X, Y, Z
```

However, a robot cannot directly use a point expressed only in the camera coordinate system.

The robot needs the same point expressed relative to its own base frame.

The purpose of Phase 04 is therefore:

```text
Camera Frame
     ↓
    TF2
     ↓
Robot Base Frame
```

This phase demonstrates the fundamental ROS 2 TF2 transformation workflow and establishes the conceptual basis for later real camera-to-robot calibration.

---

# 1. Phase 04 Goals

The goals of this phase are:

- understand ROS 2 coordinate frames
- understand parent and child frames
- understand static transformations
- publish a static TF2 transformation
- use a TF2 Buffer and TransformListener
- transform a `PointStamped`
- convert a 3D point from the camera frame into a robot base frame
- understand the difference between an example transform and real extrinsic calibration

---

# 2. Architecture

```text
ZED 2
  │
  ▼
3D Perception
  │
  ▼
Point in Camera Frame
(x, y, z)
  │
  ▼
zed_left_camera_frame
  │
  │
  │ TF2 Transform
  │ Translation + Rotation
  │
  ▼
robot_base
  │
  ▼
Point in Robot Base Frame
(x, y, z)
  │
  ▼
Future Robot Manipulation
```

The important transition is:

```text
Camera coordinates
       ↓
      TF2
       ↓
Robot coordinates
```

---

# 3. Project Directory

Phase directory:

```text
/home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_04_tf2_calibration
```

ROS 2 workspace:

```text
/home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_04_tf2_calibration/ros2_ws
```

Source structure:

```text
phase_04_tf2_calibration/
└── ros2_ws/
    └── src/
        └── zed2_tf2_calibration/
            ├── LICENSE
            ├── package.xml
            ├── setup.cfg
            ├── setup.py
            ├── resource/
            │   └── zed2_tf2_calibration
            └── zed2_tf2_calibration/
                ├── __init__.py
                ├── step01_static_tf.py
                └── step02_transform_point.py
```

Generated workspace directories are not stored in Git:

```text
build/
install/
log/
```

---

# 4. Requirements

Validated environment:

```text
OS:
Ubuntu 24.04.4 LTS

ROS:
ROS 2 Jazzy

Python:
Python 3.12

Camera used in the project:
Stereolabs ZED 2
```

ROS 2 dependencies:

```text
rclpy
geometry_msgs
tf2_ros
tf2_geometry_msgs
```

For this project environment:

```bash
export PYTHONNOUSERSITE=1
```

---

# 5. Create the ROS 2 Package

The package was created with:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning

mkdir -p phase_04_tf2_calibration/ros2_ws/src

cd phase_04_tf2_calibration/ros2_ws/src

source /opt/ros/jazzy/setup.bash

ros2 pkg create \
  zed2_tf2_calibration \
  --build-type ament_python \
  --license Apache-2.0 \
  --dependencies rclpy geometry_msgs tf2_ros tf2_geometry_msgs
```

Package:

```text
zed2_tf2_calibration
```

---

# 6. TF2 Concept

ROS 2 TF2 maintains relationships between coordinate frames.

For this phase:

```text
robot_base
    │
    │ static transform
    │
    └── zed_left_camera_frame
```

The relationship contains:

```text
Translation:
x
y
z

Rotation:
quaternion x
quaternion y
quaternion z
quaternion w
```

A complete rigid-body transformation therefore contains both:

```text
Translation + Rotation
```

---

# 7. Step 01 – Static Camera Transform

File:

```text
ros2_ws/src/zed2_tf2_calibration/zed2_tf2_calibration/step01_static_tf.py
```

The node creates a static TF relationship:

```text
robot_base
     ↓
zed_left_camera_frame
```

The values used in this learning exercise are:

```text
Translation:

x = 0.50 m
y = 0.00 m
z = 0.80 m
```

Rotation:

```text
x = 0
y = 0
z = 0
w = 1
```

This quaternion represents no rotation.

IMPORTANT:

These are deliberately chosen example values.

They are NOT measured calibration values for a real ZED 2 / robot installation.

---

# 8. Step 01 Source Code

```python
import rclpy

from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster


class StaticCameraTransform(Node):

    def __init__(self):
        super().__init__('static_camera_transform')

        self.broadcaster = StaticTransformBroadcaster(self)

        transform = TransformStamped()

        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = 'robot_base'
        transform.child_frame_id = 'zed_left_camera_frame'

        transform.transform.translation.x = 0.50
        transform.transform.translation.y = 0.00
        transform.transform.translation.z = 0.80

        transform.transform.rotation.x = 0.0
        transform.transform.rotation.y = 0.0
        transform.transform.rotation.z = 0.0
        transform.transform.rotation.w = 1.0

        self.broadcaster.sendTransform(transform)

        self.get_logger().info(
            'Published static transform: robot_base -> zed_left_camera_frame'
        )


def main(args=None):
    rclpy.init(args=args)

    node = StaticCameraTransform()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

# 9. StaticTransformBroadcaster

The important TF2 component in Step 01 is:

```python
StaticTransformBroadcaster
```

It publishes a transformation that does not continuously change.

Conceptually:

```text
Parent Frame
robot_base
     │
     │ Translation
     │ Rotation
     ▼
Child Frame
zed_left_camera_frame
```

A static transform is appropriate when the physical relationship between two frames does not change.

Example:

```text
camera rigidly mounted on robot
```

---

# 10. Step 01 Result

The node was started successfully.

Command:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_04_tf2_calibration/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash
export PYTHONNOUSERSITE=1

ros2 run zed2_tf2_calibration static_camera_tf
```

Validated output:

```text
Published static transform: robot_base -> zed_left_camera_frame
```

Therefore:

```text
StaticTransformBroadcaster     PASS

robot_base                     PASS
       ↓
zed_left_camera_frame          PASS
```

---

# 11. Step 02 – Transform a 3D Point

File:

```text
ros2_ws/src/zed2_tf2_calibration/zed2_tf2_calibration/step02_transform_point.py
```

The purpose is to transform a spatial point from:

```text
zed_left_camera_frame
```

into:

```text
robot_base
```

Architecture:

```text
PointStamped
Camera Frame

x = 1.000
y = 0.100
z = -0.050

       │
       ▼

TF2 Buffer
+
TransformListener

       │
       ▼

lookup_transform()

       │
       ▼

do_transform_point()

       │
       ▼

PointStamped
Robot Base Frame
```

---

# 12. Step 02 Source Code

```python
import rclpy

from geometry_msgs.msg import PointStamped
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from tf2_geometry_msgs import do_transform_point
from tf2_ros import Buffer, TransformException, TransformListener


class TransformPointNode(Node):

    def __init__(self):
        super().__init__('transform_point')

        self.tf_buffer = Buffer()

        self.tf_listener = TransformListener(
            self.tf_buffer,
            self,
        )

        self.timer = self.create_timer(
            1.0,
            self.transform_point,
        )

        self.done = False

    def transform_point(self):
        if self.done:
            return

        point_camera = PointStamped()

        point_camera.header.frame_id = 'zed_left_camera_frame'
        point_camera.header.stamp = self.get_clock().now().to_msg()

        point_camera.point.x = 1.00
        point_camera.point.y = 0.10
        point_camera.point.z = -0.05

        try:
            transform = self.tf_buffer.lookup_transform(
                'robot_base',
                'zed_left_camera_frame',
                Time(),
                timeout=Duration(seconds=1.0),
            )

            point_robot = do_transform_point(
                point_camera,
                transform,
            )

            self.get_logger().info(
                'Camera frame: '
                f'x={point_camera.point.x:.3f}, '
                f'y={point_camera.point.y:.3f}, '
                f'z={point_camera.point.z:.3f}'
            )

            self.get_logger().info(
                'Robot base frame: '
                f'x={point_robot.point.x:.3f}, '
                f'y={point_robot.point.y:.3f}, '
                f'z={point_robot.point.z:.3f}'
            )

            self.done = True

        except TransformException as exc:
            self.get_logger().warning(
                f'Transform not available yet: {exc}'
            )


def main(args=None):
    rclpy.init(args=args)

    node = TransformPointNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

# 13. TF2 Buffer

The TF2 Buffer stores known transformations.

```python
self.tf_buffer = Buffer()
```

Conceptually:

```text
TF Broadcasters
      │
      ▼
     /tf
   /tf_static
      │
      ▼
TF2 Buffer
```

The application can then request transformations from the buffer.

---

# 14. TransformListener

The listener receives TF information and fills the TF2 Buffer:

```python
self.tf_listener = TransformListener(
    self.tf_buffer,
    self,
)
```

Architecture:

```text
StaticTransformBroadcaster
          │
          ▼
      /tf_static
          │
          ▼
 TransformListener
          │
          ▼
       Buffer
```

---

# 15. lookup_transform()

The transformation is requested with:

```python
transform = self.tf_buffer.lookup_transform(
    'robot_base',
    'zed_left_camera_frame',
    Time(),
    timeout=Duration(seconds=1.0),
)
```

Meaning:

```text
Give me the transformation:

zed_left_camera_frame
          ↓
     robot_base
```

The first argument is the target frame:

```text
robot_base
```

The second argument is the source frame:

```text
zed_left_camera_frame
```

---

# 16. PointStamped

The input point is represented as:

```text
geometry_msgs/msg/PointStamped
```

The point contains both:

```text
coordinates
+
frame information
```

Example:

```text
frame:
zed_left_camera_frame

point:
x = 1.000
y = 0.100
z = -0.050
```

The frame is essential.

Without knowing the coordinate frame, the numbers alone do not define a useful spatial position.

---

# 17. do_transform_point()

The actual transformation is performed by:

```python
point_robot = do_transform_point(
    point_camera,
    transform,
)
```

Conceptually:

```text
P_camera
    │
    │
    │ T_robot_camera
    ▼
P_robot
```

Mathematically:

```text
P_robot = T_robot_camera × P_camera
```

For a complete rigid transform, `T` can contain both translation and rotation.

---

# 18. Validated Transformation

Input:

```text
Camera frame:

x = 1.000 m
y = 0.100 m
z = -0.050 m
```

Static translation:

```text
x = 0.500 m
y = 0.000 m
z = 0.800 m
```

Rotation:

```text
identity
```

Result:

```text
Robot base frame:

x = 1.500 m
y = 0.100 m
z = 0.750 m
```

Validated terminal output:

```text
Camera frame: x=1.000, y=0.100, z=-0.050

Robot base frame: x=1.500, y=0.100, z=0.750
```

The result is correct because no rotation was applied:

```text
Xrobot = 1.000 + 0.500
       = 1.500

Yrobot = 0.100 + 0.000
       = 0.100

Zrobot = -0.050 + 0.800
       = 0.750
```

---

# 19. Running Step 02

Two terminals are required.

## Terminal 1 – Static TF

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_04_tf2_calibration/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash
export PYTHONNOUSERSITE=1

ros2 run zed2_tf2_calibration static_camera_tf
```

Keep Terminal 1 running.

Expected:

```text
Published static transform: robot_base -> zed_left_camera_frame
```

## Terminal 2 – Transform Point

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_04_tf2_calibration/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash
export PYTHONNOUSERSITE=1

ros2 run zed2_tf2_calibration transform_point
```

Expected:

```text
Camera frame: x=1.000, y=0.100, z=-0.050
Robot base frame: x=1.500, y=0.100, z=0.750
```

---

# 20. Build Phase 04

Build command:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_04_tf2_calibration/ros2_ws

source /opt/ros/jazzy/setup.bash
export PYTHONNOUSERSITE=1

colcon build \
  --symlink-install \
  --packages-select zed2_tf2_calibration
```

Successful result:

```text
Starting >>> zed2_tf2_calibration
Finished <<< zed2_tf2_calibration

Summary: 1 package finished
```

---

# 21. Console Scripts

The relevant `setup.py` section is:

```python
entry_points={
    'console_scripts': [
        'static_camera_tf = zed2_tf2_calibration.step01_static_tf:main',
        'transform_point = zed2_tf2_calibration.step02_transform_point:main',
    ],
},
```

Therefore the two executables are:

```text
static_camera_tf
transform_point
```

---

# 22. Example Transform vs Real Calibration

This distinction is extremely important.

The transformation used in this phase:

```text
Translation:
x = 0.50
y = 0.00
z = 0.80

Rotation:
identity
```

is an educational example.

It is NOT a real camera calibration.

A real system needs the actual physical relationship between:

```text
Robot Base
     │
     ▼
Camera
```

That relationship is called an extrinsic transformation.

It contains six physical degrees of freedom:

```text
Translation:

X
Y
Z

Rotation:

Roll
Pitch
Yaw
```

In TF2, the rotation is normally represented internally as a quaternion.

---

# 23. Real Camera-to-Robot Calibration

For a real robot system, the transformation must correspond to the actual camera mounting.

Conceptually:

```text
Robot Base
     │
     │ actual measured/calibrated transform
     ▼
Camera Mount
     │
     ▼
Camera Frame
```

Depending on the physical configuration, calibration may be performed using techniques such as:

```text
extrinsic calibration

hand-eye calibration

calibration target / fiducial target

known geometric measurements
```

The correct method depends on how the camera is mounted.

---

# 24. Eye-to-Hand vs Eye-in-Hand

Two common robot camera configurations are:

## Eye-to-Hand

Camera is fixed externally:

```text
Camera
   │
   │ observes
   ▼
Robot + Workspace
```

The camera does not move with the robot arm.

The required relationship is typically between the fixed camera and robot/world base.

## Eye-in-Hand

Camera is attached to the robot:

```text
Robot Base
    │
    ▼
Robot Arm
    │
    ▼
End Effector
    │
    ▼
Camera
```

The camera moves with the robot.

This generally requires a hand-eye calibration relationship involving the robot tool/end-effector and camera.

The real calibration will be performed later when the physical camera/robot mounting is defined.

---

# 25. Relationship to Phase 03

Phase 03 produced:

```text
ZED 2
   │
   ▼
PointCloud2
   │
   ▼
3D Point
   │
   ▼
Camera Frame
```

Phase 04 adds:

```text
Camera Frame
   │
   ▼
TF2
   │
   ▼
Robot Base Frame
```

Combined:

```text
ZED 2
   │
   ▼
RGB + Depth
   │
   ▼
PointCloud2
   │
   ▼
Object / Point XYZ
   │
   ▼
Camera Frame
   │
   ▼
TF2
   │
   ▼
Robot Base Frame
```

This is the bridge between perception and manipulation.

---

# 26. Why TF2 Matters for Manipulation

Suppose perception detects an object at:

```text
Camera coordinates:

X = 0.70
Y = 0.05
Z = 0.10
```

The robot controller normally needs a position relative to a robot frame such as:

```text
base_link
```

or another defined robot base frame.

Therefore:

```text
Object Detection
       │
       ▼
Depth / PointCloud
       │
       ▼
3D Camera Coordinate
       │
       ▼
TF2
       │
       ▼
Robot Coordinate
       │
       ▼
Motion Planning
       │
       ▼
Manipulator
```

Without this transformation, perception and robot motion exist in different coordinate systems.

---

# 27. TF Tree Considerations

The ZED ROS 2 wrapper already publishes its own TF frames.

Therefore a real integrated system must maintain one consistent TF tree.

Conceptually:

```text
robot_base
     │
     ▼
camera mounting transform
     │
     ▼
ZED base/camera frames
     │
     ├── left camera frame
     ├── right camera frame
     ├── optical frames
     └── sensor frames
```

Frames must not be connected inconsistently by multiple competing transformations.

During the learning exercise, the custom static TF was tested separately so the fundamental TF2 transformation could be demonstrated clearly.

---

# 28. Generated Files

The following directories are generated by `colcon`:

```text
build/
install/
log/
```

They are not stored in Git.

Python caches are also removed:

```text
__pycache__/
*.pyc
```

The repository stores the source code required to rebuild the workspace.

---

# 29. Fresh Clone / Rebuild

After cloning the repository:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_04_tf2_calibration/ros2_ws

source /opt/ros/jazzy/setup.bash
export PYTHONNOUSERSITE=1

rosdep install \
  --from-paths src \
  --ignore-src \
  -r \
  -y

colcon build \
  --symlink-install \
  --packages-select zed2_tf2_calibration

source install/setup.bash
```

The Phase 04 nodes can then be started.

---

# 30. Phase 04 Results

```text
ROS 2 Python package                 PASS

TF2                                  PASS

StaticTransformBroadcaster           PASS

Parent / child frames                PASS

robot_base frame                     PASS

zed_left_camera_frame                PASS

TF2 Buffer                           PASS

TransformListener                    PASS

lookup_transform()                   PASS

PointStamped                         PASS

do_transform_point()                 PASS

Camera → Robot coordinate transform  PASS

Validated numeric result             PASS
```

Validated transformation:

```text
Camera:

(1.000, 0.100, -0.050)

        ↓ TF2

Robot Base:

(1.500, 0.100, 0.750)
```

---

# 31. Phase 04 Status

```text
PHASE 04 – TF2 & CALIBRATION FUNDAMENTALS

STATUS: COMPLETED
```

The TF2 workflow has been demonstrated successfully.

Real physical camera-to-robot calibration remains dependent on the final physical camera mounting and therefore is intentionally not fabricated in this phase.

The project now has the conceptual perception chain:

```text
Camera
   ↓
ROS 2
   ↓
2D Perception
   ↓
3D Perception
   ↓
TF2
   ↓
Robot Coordinate System
```

This provides the coordinate-system foundation required for later perception-to-manipulation and imitation-learning workflows.
