# Phase 02 – 2D Perception with ZED 2

## ROS 2 Perception & Imitation Learning

Phase 02 implements the first custom perception pipeline of the project.

Phase 01 validated the camera hardware, SDKs, ROS 2 wrappers, RGB, Depth, PointCloud and IMU streams.

Phase 02 now starts processing the ZED 2 RGB stream with our own ROS 2 Python code.

The goal of this phase is:

- Subscribe to the ZED 2 RGB image topic
- Convert ROS 2 images to OpenCV images with `cv_bridge`
- Display the RGB image
- Convert RGB to grayscale
- Apply Gaussian blur
- Perform Canny edge detection
- Detect contours
- Draw bounding boxes
- Publish the processed result as a new ROS 2 image topic

No AI model is used in this phase.

AI object detection is intentionally reserved for a later phase.

---

# 1. Phase 02 Architecture

```text
ZED 2
  │
  ▼
ZED SDK
  │
  ▼
zed-ros2-wrapper
  │
  ▼
ROS 2 Jazzy
  │
  ▼
/zed/zed_node/rgb/color/rect/image
  │
  ▼
sensor_msgs/msg/Image
  │
  ▼
zed2_perception
  │
  ▼
cv_bridge
  │
  ▼
OpenCV
  │
  ├── RGB
  │
  ├── Grayscale
  │
  ├── Gaussian Blur
  │
  ├── Canny Edge Detection
  │
  ├── Contour Detection
  │
  └── Bounding Boxes
  │
  ▼
/perception/two_d/image
```

---

# 2. Project Directory

Phase 02 directory:

```text
/home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_02_2d_perception
```

ROS 2 workspace:

```text
/home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_02_2d_perception/ros2_ws
```

Source structure:

```text
phase_02_2d_perception/
└── ros2_ws/
    └── src/
        └── zed2_perception/
            ├── LICENSE
            ├── package.xml
            ├── setup.cfg
            ├── setup.py
            ├── resource/
            │   └── zed2_perception
            ├── test/
            │   ├── test_copyright.py
            │   ├── test_flake8.py
            │   └── test_pep257.py
            └── zed2_perception/
                ├── __init__.py
                ├── step01_zed_rgb_viewer.py
                └── step02_2d_perception.py
```

Generated ROS 2 directories are not stored in Git:

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

System NumPy:
1.26.4

OpenCV:
4.6.0

cv_bridge:
ROS 2 Jazzy package

GPU:
NVIDIA GeForce RTX 5090 Laptop GPU
```

Required ROS 2 dependencies:

```text
rclpy
sensor_msgs
cv_bridge
```

Required Python/OpenCV component:

```text
cv2
```

---

# 4. Important Python Environment Requirement

The user Python environment contained:

```text
NumPy 2.5.1
```

from:

```text
~/.local/lib/python3.12/site-packages
```

The ROS 2 Jazzy OpenCV and `cv_bridge` stack on this system was compiled against NumPy 1.x.

This caused an incompatibility when importing OpenCV:

```text
A module that was compiled using NumPy 1.x
cannot be run in NumPy 2.x
```

The solution used for Phase 02 is:

```bash
export PYTHONNOUSERSITE=1
```

This prevents Python from loading packages from the user site directory for the current terminal.

The resulting validated Python stack is:

```text
Python:
3.12.3

NumPy:
1.26.4

NumPy path:
/usr/lib/python3/dist-packages/numpy

OpenCV:
4.6.0

OpenCV path:
/usr/lib/python3/dist-packages/cv2.cpython-312-x86_64-linux-gnu.so

cv_bridge:
OK
```

This avoids modifying or downgrading the separate user Python environment.

For ROS 2 perception terminals in this phase, use:

```bash
export PYTHONNOUSERSITE=1
```

---

# 5. Create the ROS 2 Package

Create the workspace:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_02_2d_perception

mkdir -p ros2_ws/src
```

Source ROS 2:

```bash
source /opt/ros/jazzy/setup.bash
```

Create the Python package:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_02_2d_perception/ros2_ws/src

ros2 pkg create \
  zed2_perception \
  --build-type ament_python \
  --license Apache-2.0 \
  --dependencies rclpy sensor_msgs cv_bridge
```

The created package is:

```text
zed2_perception
```

---

# 6. Validate OpenCV and cv_bridge

Use:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_02_2d_perception

source /opt/ros/jazzy/setup.bash
export PYTHONNOUSERSITE=1

echo "=== PYTHON ==="
which python3
python3 --version

echo
echo "=== NUMPY ==="
python3 -c "import numpy; print('NumPy:', numpy.__version__); print('Path:', numpy.__file__)"

echo
echo "=== OPENCV ==="
python3 -c "import cv2; print('OpenCV:', cv2.__version__); print('Path:', cv2.__file__)"

echo
echo "=== CV BRIDGE ==="
python3 -c "from cv_bridge import CvBridge; print('cv_bridge: OK')"
```

Validated result:

```text
Python 3.12.3

NumPy:
1.26.4

OpenCV:
4.6.0

cv_bridge:
OK
```

---

# 7. Step 01 – ZED RGB Viewer

File:

```text
ros2_ws/src/zed2_perception/zed2_perception/step01_zed_rgb_viewer.py
```

Purpose:

```text
ZED 2
  ↓
ROS 2 RGB Topic
  ↓
sensor_msgs/Image
  ↓
cv_bridge
  ↓
OpenCV
  ↓
Live RGB Window
```

Source code:

```python
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


class ZedRgbViewer(Node):

    def __init__(self):
        super().__init__('zed_rgb_viewer')

        self.bridge = CvBridge()
        self.first_frame_received = False

        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.subscription = self.create_subscription(
            Image,
            '/zed/zed_node/rgb/color/rect/image',
            self.image_callback,
            qos,
        )

        self.get_logger().info(
            'Listening to /zed/zed_node/rgb/color/rect/image'
        )

    def image_callback(self, msg):

        if not self.first_frame_received:
            self.get_logger().info(
                f'First RGB frame received: '
                f'{msg.width}x{msg.height}, encoding={msg.encoding}'
            )
            self.first_frame_received = True

        try:
            image = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8',
            )

            cv2.imshow(
                'ZED 2 - ROS 2 RGB',
                image,
            )

            cv2.waitKey(1)

        except Exception as exc:
            self.get_logger().error(
                f'Image conversion failed: {exc}'
            )

    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = ZedRgbViewer()

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

Validated input:

```text
Topic:
/zed/zed_node/rgb/color/rect/image

Type:
sensor_msgs/msg/Image

Resolution:
1280x720

Encoding:
bgra8
```

The node converts the incoming image to:

```text
bgr8
```

for OpenCV.

---

# 8. Step 02 – 2D Perception Node

File:

```text
ros2_ws/src/zed2_perception/zed2_perception/step02_2d_perception.py
```

Purpose:

```text
RGB
 ↓
Grayscale
 ↓
Gaussian Blur
 ↓
Canny
 ↓
Contours
 ↓
Bounding Boxes
 ↓
Processed ROS 2 Image
```

Source code:

```python
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


class Zed2DPerception(Node):

    def __init__(self):
        super().__init__('zed_2d_perception')

        self.bridge = CvBridge()

        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.subscription = self.create_subscription(
            Image,
            '/zed/zed_node/rgb/color/rect/image',
            self.image_callback,
            qos,
        )

        self.processed_publisher = self.create_publisher(
            Image,
            '/perception/two_d/image',
            10,
        )

        self.get_logger().info(
            '2D perception node started'
        )

    def image_callback(self, msg):

        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8',
            )

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY,
            )

            blurred = cv2.GaussianBlur(
                gray,
                (5, 5),
                0,
            )

            edges = cv2.Canny(
                blurred,
                50,
                150,
            )

            contours, _ = cv2.findContours(
                edges,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE,
            )

            result = frame.copy()

            for contour in contours:

                area = cv2.contourArea(contour)

                if area < 500:
                    continue

                x, y, width, height = cv2.boundingRect(contour)

                cv2.rectangle(
                    result,
                    (x, y),
                    (x + width, y + height),
                    (0, 255, 0),
                    2,
                )

                cv2.putText(
                    result,
                    f'Area: {int(area)}',
                    (x, max(y - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
                )

            cv2.imshow(
                'ZED 2 - RGB',
                frame,
            )

            cv2.imshow(
                'ZED 2 - Grayscale',
                gray,
            )

            cv2.imshow(
                'ZED 2 - Canny Edges',
                edges,
            )

            cv2.imshow(
                'ZED 2 - 2D Perception',
                result,
            )

            cv2.waitKey(1)

            processed_msg = self.bridge.cv2_to_imgmsg(
                result,
                encoding='bgr8',
            )

            processed_msg.header = msg.header

            self.processed_publisher.publish(
                processed_msg
            )

        except Exception as exc:
            self.get_logger().error(
                f'2D perception failed: {exc}'
            )

    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = Zed2DPerception()

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

# 9. OpenCV Processing Steps

## RGB Input

The original camera image is received from:

```text
/zed/zed_node/rgb/color/rect/image
```

---

## Grayscale

Conversion:

```python
gray = cv2.cvtColor(
    frame,
    cv2.COLOR_BGR2GRAY,
)
```

Purpose:

```text
Reduce the image from three color channels
to one intensity channel.
```

This simplifies later image processing.

---

## Gaussian Blur

```python
blurred = cv2.GaussianBlur(
    gray,
    (5, 5),
    0,
)
```

Purpose:

```text
Reduce image noise before edge detection.
```

---

## Canny Edge Detection

```python
edges = cv2.Canny(
    blurred,
    50,
    150,
)
```

Purpose:

```text
Detect strong intensity transitions
that correspond to visual edges.
```

---

## Contour Detection

```python
contours, _ = cv2.findContours(
    edges,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
)
```

Purpose:

```text
Convert groups of connected edges
into candidate object regions.
```

---

## Noise Filtering

Small contours are ignored:

```python
if area < 500:
    continue
```

This prevents many very small edge regions from being treated as useful objects.

---

## Bounding Boxes

For each accepted contour:

```python
x, y, width, height = cv2.boundingRect(contour)
```

A rectangle is drawn around the region:

```python
cv2.rectangle(
    result,
    (x, y),
    (x + width, y + height),
    (0, 255, 0),
    2,
)
```

The contour area is also displayed.

---

# 10. Processed ROS 2 Output Topic

The resulting image is converted back into a ROS 2 image:

```python
processed_msg = self.bridge.cv2_to_imgmsg(
    result,
    encoding='bgr8',
)
```

The original timestamp and frame information are retained:

```python
processed_msg.header = msg.header
```

The result is published on:

```text
/perception/two_d/image
```

Important:

ROS 2 topic name tokens must not start with a number.

Therefore the valid topic is:

```text
/perception/two_d/image
```

---

# 11. setup.py Console Scripts

The package contains two executable ROS 2 nodes.

Relevant `setup.py` section:

```python
entry_points={
    'console_scripts': [
        'zed_rgb_viewer = zed2_perception.step01_zed_rgb_viewer:main',
        'zed_2d_perception = zed2_perception.step02_2d_perception:main',
    ],
},
```

Available commands:

```text
ros2 run zed2_perception zed_rgb_viewer
```

and:

```text
ros2 run zed2_perception zed_2d_perception
```

---

# 12. Build Phase 02

From the workspace:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_02_2d_perception/ros2_ws

source /opt/ros/jazzy/setup.bash
export PYTHONNOUSERSITE=1

colcon build \
  --symlink-install \
  --packages-select zed2_perception
```

Successful build:

```text
Starting >>> zed2_perception
Finished <<< zed2_perception

Summary: 1 package finished
```

A setuptools warning related to `pytest-repeat` was displayed during the build.

It did not prevent the package from building successfully.

---

# 13. Start Phase 02

Two terminals are required.

## Terminal 1 – Start ZED 2

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash
export PYTHONNOUSERSITE=1

ros2 launch zed_wrapper zed_camera.launch.py \
  camera_model:=zed2
```

The ZED ROS 2 wrapper must remain running.

---

## Terminal 2 – Start the RGB Viewer

To run Step 01:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_02_2d_perception/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash
export PYTHONNOUSERSITE=1

ros2 run zed2_perception zed_rgb_viewer
```

Validated output:

```text
Listening to /zed/zed_node/rgb/color/rect/image
First RGB frame received: 1280x720, encoding=bgra8
```

An OpenCV live image window opens successfully.

---

## Terminal 2 – Start 2D Perception

To run the complete Phase 02 pipeline:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_02_2d_perception/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash
export PYTHONNOUSERSITE=1

ros2 run zed2_perception zed_2d_perception
```

Four OpenCV windows are displayed:

```text
ZED 2 - RGB

ZED 2 - Grayscale

ZED 2 - Canny Edges

ZED 2 - 2D Perception
```

The final window shows detected contour regions and bounding boxes.

---

# 14. Validated Phase 02 Data Flow

The complete tested pipeline is:

```text
Stereolabs ZED 2
        │
        ▼
ZED SDK 5.4.1
        │
        ▼
zed-ros2-wrapper
        │
        ▼
ROS 2 Jazzy
        │
        ▼
/zed/zed_node/rgb/color/rect/image
        │
        ▼
sensor_msgs/msg/Image
        │
        ▼
Zed2DPerception Node
        │
        ▼
cv_bridge
        │
        ▼
OpenCV BGR Image
        │
        ├── Grayscale
        │
        ├── Gaussian Blur
        │
        ├── Canny Edge Detection
        │
        ├── Contour Detection
        │
        └── Bounding Boxes
        │
        ▼
Processed OpenCV Image
        │
        ▼
cv_bridge
        │
        ▼
sensor_msgs/msg/Image
        │
        ▼
/perception/two_d/image
```

---

# 15. Phase 02 Results

```text
ROS 2 Python package             PASS

ZED RGB subscription             PASS

sensor_msgs/Image                PASS

cv_bridge                        PASS

OpenCV                           PASS

RGB display                      PASS

Grayscale                        PASS

Gaussian Blur                    PASS

Canny Edge Detection             PASS

Contour Detection                PASS

Bounding Boxes                   PASS

Processed ROS 2 image publisher  PASS
```

---

# 16. What Was Learned

Phase 01 showed:

```text
Camera
→ SDK
→ ROS 2 Driver
→ ROS 2 Topics
```

Phase 02 adds our own software:

```text
ROS 2 Image
→ Python
→ cv_bridge
→ OpenCV
→ Image Processing
→ Perception Result
```

This is the first phase in the project where our own perception code processes real camera data.

---

# 17. Git Rules

Only source code and project documentation belong in Git.

Keep:

```text
ros2_ws/src/
README.md
```

Do not commit:

```text
ros2_ws/build/
ros2_ws/install/
ros2_ws/log/
__pycache__/
*.pyc
```

These directories are generated locally and can be recreated with `colcon build`.

---

# 18. Rebuild After a Fresh Git Clone

Because `build/`, `install/` and `log/` are intentionally not stored in Git, rebuild Phase 02 after cloning:

```bash
cd /home/sarvg/projects/robotics/ros2_perception_imitation_learning/phase_02_2d_perception/ros2_ws

source /opt/ros/jazzy/setup.bash
export PYTHONNOUSERSITE=1

rosdep install \
  --from-paths src \
  --ignore-src \
  -r \
  -y

colcon build \
  --symlink-install \
  --packages-select zed2_perception
```

Then:

```bash
source install/setup.bash
```

The package is ready to run.

---

# 19. Phase 02 Completed

```text
PHASE 02 – 2D PERCEPTION

STATUS: COMPLETED
```

Validated camera:

```text
Stereolabs ZED 2
```

Validated custom ROS 2 nodes:

```text
zed_rgb_viewer

zed_2d_perception
```

Validated output:

```text
Live RGB
Grayscale
Canny Edges
Contour Detection
Bounding Boxes
Processed ROS 2 Image
```

---

# 20. Next Phase

Next:

```text
Phase 03 – 3D Perception
```

The next architecture will extend the current RGB pipeline with depth and 3D data:

```text
ZED 2
  │
  ├── RGB
  │
  ├── Depth
  │
  └── PointCloud
        │
        ▼
    3D Perception
```

Phase 03 will focus on actual spatial information rather than only 2D image coordinates.
