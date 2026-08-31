# Phase 03 – 3D Perception with ZED 2

## ROS 2 Perception & Imitation Learning

Phase 03 extends the project from 2D image processing into actual 3D perception.

Phase 02 processed RGB images with OpenCV and produced:

- grayscale images
- blurred images
- Canny edges
- contours
- bounding boxes

Phase 03 adds spatial information from the ZED 2.

The goals are:

- read registered depth images
- determine real distance values in meters
- read `sensor_msgs/msg/PointCloud2`
- extract a real 3D point
- understand the ZED/ROS coordinate system
- visualize the complete 3D point cloud in RViz2

---

# 1. Phase 03 Architecture

```text
ZED 2
  │
  ▼
Stereo Cameras
  │
  ▼
ZED SDK Depth Processing
  │
  ├──────────────────────────────┐
  │                              │
  ▼                              ▼
Registered Depth            Registered PointCloud
  │                              │
  ▼                              ▼
sensor_msgs/Image          sensor_msgs/PointCloud2
  │                              │
  ▼                              ▼
Depth Distance Node        PointCloud XYZ Node
  │                              │
  ▼                              ▼
Distance in meters         3D Point (X,Y,Z)
                                 │
                                 ▼
                               RViz2
                                 │
                                 ▼
                        Full 3D Point Cloud
```

---

# 2. Project Directory

Phase directory:

```text
/home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_03_3d_perception
```

ROS 2 workspace:

```text
/home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_03_3d_perception/ros2_ws
```

Source structure:

```text
phase_03_3d_perception/
└── ros2_ws/
    └── src/
        └── zed2_3d_perception/
            ├── LICENSE
            ├── package.xml
            ├── setup.cfg
            ├── setup.py
            ├── resource/
            │   └── zed2_3d_perception
            ├── test/
            │   ├── test_copyright.py
            │   ├── test_flake8.py
            │   └── test_pep257.py
            └── zed2_3d_perception/
                ├── __init__.py
                ├── step01_depth_distance.py
                └── step02_pointcloud_xyz.py
```

Generated workspace directories are not stored in Git:

```text
build/
install/
log/
```

---

# 3. Requirements

Validated environment:

```text
OS:
Ubuntu 24.04.4 LTS

ROS:
ROS 2 Jazzy

Camera:
Stereolabs ZED 2

ZED SDK:
5.4.1

Python:
3.12.3

NumPy:
1.26.4

OpenCV:
4.6.0

GPU:
NVIDIA GeForce RTX 5090 Laptop GPU
```

Required ROS 2 dependencies:

```text
rclpy
sensor_msgs
sensor_msgs_py
cv_bridge
```

For this ROS 2 perception environment:

```bash
export PYTHONNOUSERSITE=1
```

This avoids loading incompatible user-installed NumPy packages from:

```text
~/.local/lib/python3.12/site-packages
```

---

# 4. Create the ROS 2 Package

Create the workspace:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_03_3d_perception

mkdir -p ros2_ws/src
```

Source ROS 2:

```bash
source /opt/ros/jazzy/setup.bash
```

Create the package:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_03_3d_perception/ros2_ws/src

ros2 pkg create \
  zed2_3d_perception \
  --build-type ament_python \
  --license Apache-2.0 \
  --dependencies rclpy sensor_msgs cv_bridge
```

The package name is:

```text
zed2_3d_perception
```

---

# 5. Important ZED 2 Topics

Registered depth:

```text
/zed/zed_node/depth/depth_registered
```

Message type:

```text
sensor_msgs/msg/Image
```

Registered point cloud:

```text
/zed/zed_node/point_cloud/cloud_registered
```

Message type:

```text
sensor_msgs/msg/PointCloud2
```

---

# 6. Step 01 – Depth Distance

File:

```text
ros2_ws/src/zed2_3d_perception/zed2_3d_perception/step01_depth_distance.py
```

Purpose:

```text
Depth Image
   ↓
Center Pixel
   ↓
32-bit Floating Point Depth
   ↓
Distance in meters
```

The node subscribes to:

```text
/zed/zed_node/depth/depth_registered
```

The ZED registered depth image uses:

```text
32FC1
```

This means:

```text
32-bit floating point
1 channel
```

Each valid pixel therefore contains a real depth value.

---

# 7. Step 01 Source Code

```python
import math

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    QoSReliabilityPolicy,
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
)
from sensor_msgs.msg import Image


class ZedDepthDistance(Node):

    def __init__(self):
        super().__init__('zed_depth_distance')

        self.bridge = CvBridge()

        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.subscription = self.create_subscription(
            Image,
            '/zed/zed_node/depth/depth_registered',
            self.depth_callback,
            qos,
        )

        self.get_logger().info(
            'Listening to /zed/zed_node/depth/depth_registered'
        )

    def depth_callback(self, msg):
        try:
            depth_image = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='32FC1',
            )

            height, width = depth_image.shape

            center_x = width // 2
            center_y = height // 2

            distance_m = float(depth_image[center_y, center_x])

            if math.isfinite(distance_m):
                text = f'Distance: {distance_m:.3f} m'
            else:
                text = 'Distance: invalid'

            display = cv2.normalize(
                depth_image,
                None,
                0,
                255,
                cv2.NORM_MINMAX,
            )

            display = display.astype('uint8')

            display = cv2.applyColorMap(
                display,
                cv2.COLORMAP_JET,
            )

            cv2.drawMarker(
                display,
                (center_x, center_y),
                (255, 255, 255),
                cv2.MARKER_CROSS,
                20,
                2,
            )

            cv2.putText(
                display,
                text,
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                'ZED 2 - Depth Distance',
                display,
            )

            cv2.waitKey(1)

        except Exception as exc:
            self.get_logger().error(
                f'Depth processing failed: {exc}'
            )

    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = ZedDepthDistance()

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

# 8. Depth Distance Result

The node successfully displayed a colorized depth image.

A white cross marked the center measurement point.

A validated example measurement was:

```text
Distance: 1.156 m
```

This proves:

```text
ZED 2
  ↓
Stereo Depth
  ↓
ROS 2 Depth Image
  ↓
Pixel
  ↓
Real Distance in meters
```

---

# 9. Depth Invalid Values

Depth cameras can produce pixels with:

```text
NaN
Inf
invalid depth
```

This can happen when:

- stereo matching is uncertain
- surfaces have poor texture
- reflections occur
- the point is outside the reliable measurement range
- motion causes temporary uncertainty

During visualization, a warning appeared:

```text
RuntimeWarning: invalid value encountered in cast
```

The depth calculation itself still worked.

This warning is related to invalid pixels inside the visualization image and does not invalidate the measured valid center depth.

---

# 10. Step 02 – PointCloud XYZ

File:

```text
ros2_ws/src/zed2_3d_perception/zed2_3d_perception/step02_pointcloud_xyz.py
```

Purpose:

```text
PointCloud2
   ↓
Organized Point Cloud
   ↓
Center Pixel
   ↓
Linear Point Index
   ↓
X, Y, Z
```

The node subscribes to:

```text
/zed/zed_node/point_cloud/cloud_registered
```

---

# 11. Organized Point Cloud

The ZED PointCloud2 message is organized.

The tested point cloud had a center pixel:

```text
u = 224
v = 128
```

This corresponds to a cloud resolution of approximately:

```text
448 x 256
```

For an organized point cloud, the linear point index is:

```text
index = v * width + u
```

This is used to select one point from the PointCloud2 message.

---

# 12. Step 02 Source Code

```python
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    QoSReliabilityPolicy,
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
)
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2


class ZedPointCloudXYZ(Node):

    def __init__(self):
        super().__init__('zed_pointcloud_xyz')

        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.subscription = self.create_subscription(
            PointCloud2,
            '/zed/zed_node/point_cloud/cloud_registered',
            self.pointcloud_callback,
            qos,
        )

        self.get_logger().info(
            'Listening to /zed/zed_node/point_cloud/cloud_registered'
        )

    def pointcloud_callback(self, msg):
        center_u = msg.width // 2
        center_v = msg.height // 2

        center_index = center_v * msg.width + center_u

        points = point_cloud2.read_points(
            msg,
            field_names=('x', 'y', 'z'),
            skip_nans=False,
            uvs=[center_index],
        )

        if len(points) == 0:
            self.get_logger().info('Center point: unavailable')
            return

        point = points[0]

        x = float(point['x'])
        y = float(point['y'])
        z = float(point['z'])

        if all(math.isfinite(value) for value in (x, y, z)):
            self.get_logger().info(
                f'Center pixel ({center_u}, {center_v}) -> '
                f'x={x:.3f} m, '
                f'y={y:.3f} m, '
                f'z={z:.3f} m'
            )
        else:
            self.get_logger().info(
                f'Center pixel ({center_u}, {center_v}) -> invalid 3D point'
            )


def main(args=None):
    rclpy.init(args=args)

    node = ZedPointCloudXYZ()

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

# 13. ZED / ROS Coordinate System

The point cloud is expressed in a ROS-compatible coordinate frame.

For the tested ZED ROS setup:

```text
X = forward
Y = lateral
Z = vertical
```

Example:

```text
x = 1.319 m
y = 0.067 m
z = -0.038 m
```

Interpretation:

```text
X:
approximately 1.319 m in front of the camera

Y:
approximately 0.067 m lateral offset

Z:
approximately 0.038 m below the camera reference axis
```

This is fundamentally different from a 2D pixel coordinate.

A 2D pixel only tells us:

```text
u, v
```

A PointCloud2 point tells us:

```text
X, Y, Z
```

in real spatial coordinates.

---

# 14. PointCloud Movement Test

The camera was moved closer to and farther from the observed scene.

The X coordinate changed accordingly.

Examples:

```text
x = 1.319 m
x = 1.543 m
x = 1.186 m
x = 1.105 m
x = 0.901 m
x = 0.771 m
x = 0.688 m
x = 0.587 m
```

Later values included:

```text
x = 1.828 m
x = 1.737 m
x = 1.291 m
x = 1.053 m
x = 0.978 m
x = 0.712 m
x = 0.588 m
```

This confirms that the PointCloud2 measurements respond to real movement in the scene.

---

# 15. Invalid PointCloud Points

During motion, some samples returned:

```text
invalid 3D point
```

This is expected behavior for stereo-derived point clouds.

Possible reasons include:

- temporary stereo mismatch
- insufficient texture
- occlusion
- object edges
- fast camera movement
- reflective surfaces
- missing depth data

The important result is that valid XYZ points immediately returned again.

Therefore the PointCloud2 pipeline itself was functioning correctly.

---

# 16. setup.py Console Scripts

The package contains two executable nodes.

Relevant `setup.py` section:

```python
entry_points={
    'console_scripts': [
        'zed_depth_distance = zed2_3d_perception.step01_depth_distance:main',
        'zed_pointcloud_xyz = zed2_3d_perception.step02_pointcloud_xyz:main',
    ],
},
```

Available commands:

```text
ros2 run zed2_3d_perception zed_depth_distance
```

and:

```text
ros2 run zed2_3d_perception zed_pointcloud_xyz
```

---

# 17. Build Phase 03

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_03_3d_perception/ros2_ws

source /opt/ros/jazzy/setup.bash
export PYTHONNOUSERSITE=1

colcon build \
  --symlink-install \
  --packages-select zed2_3d_perception
```

Successful result:

```text
Starting >>> zed2_3d_perception
Finished <<< zed2_3d_perception

Summary: 1 package finished
```

A setuptools warning related to `pytest-repeat` appeared during build.

It did not prevent the package from building successfully.

---

# 18. Terminal 1 – Start ZED 2

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash
export PYTHONNOUSERSITE=1

ros2 launch zed_wrapper zed_camera.launch.py \
  camera_model:=zed2
```

Keep this terminal running.

---

# 19. Terminal 2 – Run Depth Distance

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_03_3d_perception/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash
export PYTHONNOUSERSITE=1

ros2 run zed2_3d_perception zed_depth_distance
```

Expected window:

```text
ZED 2 - Depth Distance
```

The window displays:

- colorized depth image
- center marker
- distance in meters

---

# 20. Terminal 2 – Run PointCloud XYZ

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_03_3d_perception/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash
export PYTHONNOUSERSITE=1

ros2 run zed2_3d_perception zed_pointcloud_xyz
```

Example output:

```text
Center pixel (224, 128) ->
x=1.319 m,
y=0.067 m,
z=-0.038 m
```

This node intentionally prints XYZ values to the terminal.

It does not open an OpenCV window.

---

# 21. Step 03 – Visualize PointCloud2 in RViz2

No additional custom Python node is required for this step.

RViz2 is used to visualize the complete point cloud.

Start ZED 2 in Terminal 1.

Then in Terminal 2:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_03_3d_perception/ros2_ws

source /opt/ros/jazzy/setup.bash
export PYTHONNOUSERSITE=1

rviz2
```

---

# 22. RViz2 Configuration

Set:

```text
Global Options
  Fixed Frame:
  zed_left_camera_frame
```

Add:

```text
PointCloud2
```

Set the PointCloud2 topic to:

```text
/zed/zed_node/point_cloud/cloud_registered
```

Validated PointCloud2 configuration:

```text
Status:
Ok

Reliability Policy:
Reliable

Durability Policy:
Volatile

History Policy:
Keep Last

Position Transformer:
XYZ

Color Transformer:
RGB8
```

The point cloud appeared successfully.

---

# 23. RViz2 PointCloud Result

RViz2 successfully displayed the real room as a colored 3D point cloud.

Visible structures included:

- person
- walls
- furniture
- table
- room geometry
- nearby objects

The visualization contained tens of thousands of spatial points per frame.

Observed examples included approximately:

```text
85,774 points
```

and during another view approximately:

```text
92,726 points
```

The PointCloud2 stream was received at approximately:

```text
10 Hz
```

The RViz status showed:

```text
PointCloud2:
Status: Ok

Transform:
Ok
```

This proves that the full spatial point cloud pipeline is functional.

---

# 24. Complete Phase 03 Data Flow

```text
                       ZED 2
                         │
                         ▼
                  Stereo Cameras
                         │
                         ▼
                  ZED SDK 5.4.1
                         │
           ┌─────────────┴─────────────┐
           │                           │
           ▼                           ▼
    Registered Depth            Registered PointCloud
           │                           │
           ▼                           ▼
 sensor_msgs/Image          sensor_msgs/PointCloud2
           │                           │
           ▼                           ▼
 step01_depth_distance      step02_pointcloud_xyz
           │                           │
           ▼                           ▼
 Distance in meters              X, Y, Z
                                       │
                                       ▼
                                     RViz2
                                       │
                                       ▼
                              Full 3D Environment
```

---

# 25. Difference Between Phase 02 and Phase 03

Phase 02:

```text
Image pixel
   ↓
u, v
   ↓
2D image processing
```

Phase 03:

```text
Image / Depth / PointCloud
   ↓
real spatial information
   ↓
X, Y, Z
```

Phase 02 can answer:

```text
Where is something in the image?
```

Phase 03 can answer:

```text
Where is something in 3D space?
How far away is it?
What is its spatial position?
```

This is essential for robot manipulation.

---

# 26. Why Point Clouds Matter for Robotics

A robot cannot manipulate an object using only a 2D bounding box.

A typical manipulation pipeline requires:

```text
Object Detection
        │
        ▼
2D Region
        │
        ▼
Depth / PointCloud
        │
        ▼
3D Position
        │
        ▼
TF2
        │
        ▼
Robot Coordinate System
        │
        ▼
Motion Planning
        │
        ▼
Grasp / Manipulation
```

Phase 03 therefore creates the 3D foundation for later manipulation phases.

---

# 27. Git Rules

Store:

```text
phase_03_3d_perception/README.md
phase_03_3d_perception/ros2_ws/src/
```

Do not store:

```text
phase_03_3d_perception/ros2_ws/build/
phase_03_3d_perception/ros2_ws/install/
phase_03_3d_perception/ros2_ws/log/
__pycache__/
*.pyc
```

These are generated locally.

---

# 28. Fresh Clone / Rebuild

After cloning the project:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_03_3d_perception/ros2_ws

source /opt/ros/jazzy/setup.bash
export PYTHONNOUSERSITE=1

rosdep install \
  --from-paths src \
  --ignore-src \
  -r \
  -y

colcon build \
  --symlink-install \
  --packages-select zed2_3d_perception
```

Then:

```bash
source install/setup.bash
```

Phase 03 is ready to run.

---

# 29. Phase 03 Results

```text
ROS 2 Python package          PASS

Registered Depth             PASS

32FC1 Depth Image            PASS

Distance in meters           PASS

PointCloud2                  PASS

Organized Point Cloud        PASS

Center point extraction      PASS

XYZ coordinates              PASS

Movement test                PASS

Invalid-point handling       PASS

RViz2                        PASS

3D PointCloud visualization  PASS

TF / Transform               PASS
```

---

# 30. Phase 03 Completed

```text
PHASE 03 – 3D PERCEPTION

STATUS: COMPLETED
```

Validated camera:

```text
Stereolabs ZED 2
```

Validated ROS 2 topics:

```text
/zed/zed_node/depth/depth_registered

/zed/zed_node/point_cloud/cloud_registered
```

Validated custom nodes:

```text
zed_depth_distance

zed_pointcloud_xyz
```

Validated visualization:

```text
RViz2 PointCloud2
```

---

# 31. Next Phase

Next:

```text
Phase 04 – TF2 & Calibration
```

The next step is to connect camera coordinates to robot/world coordinates.

Conceptually:

```text
Camera Point
(X,Y,Z)
   │
   ▼
Camera Frame
   │
   ▼
TF2
   │
   ▼
Robot / Base Frame
   │
   ▼
Usable Robot Coordinate
```

This is the bridge between perception and later manipulation.
