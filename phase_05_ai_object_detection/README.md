# Phase 05 - AI Object Detection & 3D Object Localization

## ROS 2 Perception & Imitation Learning

Phase 05 combines the perception pipeline created in the previous phases.

The goal is no longer to measure only an arbitrary image pixel.

Instead, the system detects real objects, determines their 3D position and finally transforms the detected object position from the ZED camera coordinate system into a robot coordinate system.

The complete pipeline is:

```text
ZED 2
  ↓
RGB Image
  ↓
Object Detection
  ↓
2D Bounding Box
  ↓
3D Object Position
  ↓
zed_left_camera_frame
  ↓
TF2
  ↓
robot_base
```

---

# 1. Phase 05 Goals

The goals of Phase 05 are:

- convert a 2D image pixel into a 3D point
- understand pixel + depth → XYZ
- detect a simple object using classical computer vision
- determine the 3D position of the detected object
- use the native ZED AI Object Detection
- consume `zed_msgs/msg/ObjectsStamped`
- obtain AI-detected object classes such as `Laptop` and `Person`
- understand the ZED TF tree
- transform detected object coordinates from the camera frame into `robot_base`

---

# 2. Project Structure

```text
phase_05_ai_object_detection/
├── README.md
└── ros2_ws/
    └── src/
        └── zed2_object_localization/
            ├── LICENSE
            ├── package.xml
            ├── resource/
            │   └── zed2_object_localization
            ├── setup.cfg
            ├── setup.py
            └── zed2_object_localization/
                ├── __init__.py
                ├── step01_pixel_to_3d.py
                ├── step02_object_to_3d.py
                ├── step03_zed_object_detection.py
                └── step04_object_to_robot_frame.py
```

---

# 3. ROS 2 Environment

The project uses:

```text
ROS 2: Jazzy
Camera: Stereolabs ZED 2
ROS_DOMAIN_ID: 30
RMW: Fast DDS
```

The ZED ROS 2 workspace from Phase 01 is:

```text
~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws
```

The Phase 05 workspace is:

```text
~/projects/robotics/ros2_perception_imitation_learning/phase_05_ai_object_detection/ros2_ws
```

---

# 4. Build Phase 05

Build the package with:

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning/phase_05_ai_object_detection/ros2_ws

source /opt/ros/jazzy/setup.bash
source ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws/install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1

colcon build \
  --symlink-install \
  --packages-select zed2_object_localization
```

---

# 5. Example 01 - Pixel to 3D

File:

```text
zed2_object_localization/step01_pixel_to_3d.py
```

The first example demonstrates the fundamental relationship:

```text
2D Pixel
+
Depth
+
Camera Intrinsics
=
3D Point
```

The center pixel of the image is selected and converted into a 3D coordinate.

Example result:

```text
Pixel (640, 360)
    ↓
X = -0.049 m
Y =  0.028 m
Z =  0.958 m
```

This means that the selected image pixel corresponds to a physical point approximately 0.96 m away from the camera.

## Example 01 - Terminal 1

Start the ZED 2 camera.

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1

ros2 launch zed_wrapper zed_camera.launch.py \
  camera_model:=zed2
```

Leave Terminal 1 running.

## Example 01 - Terminal 2

Run the pixel-to-3D node.

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning/phase_05_ai_object_detection/ros2_ws

source /opt/ros/jazzy/setup.bash
source ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws/install/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1

ros2 run zed2_object_localization pixel_to_3d
```

Example output:

```text
Pixel (640, 360) -> X=-0.049 m, Y=0.028 m, Z=0.958 m
```

---

# 6. Example 02 - Classical Object Detection to 3D

File:

```text
zed2_object_localization/step02_object_to_3d.py
```

The second example extends the first example.

Instead of selecting a fixed pixel, an object is detected in the RGB image.

The pipeline is:

```text
RGB Image
   ↓
Object Detection
   ↓
Bounding Box
   ↓
Bounding Box Center
   ↓
Depth
   ↓
3D Position
```

The program displays the detected object using an OpenCV window.

The detected object's center pixel is combined with depth information to calculate the 3D position.

Example:

```text
Object center (505, 188)
    ↓
X = -0.187 m
Y = -0.239 m
Z =  0.971 m
```

## Example 02 - Terminal 1

Start the ZED 2 camera.

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1

ros2 launch zed_wrapper zed_camera.launch.py \
  camera_model:=zed2
```

Leave Terminal 1 running.

## Example 02 - Terminal 2

Run the classical object detection and 3D localization node.

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning/phase_05_ai_object_detection/ros2_ws

source /opt/ros/jazzy/setup.bash
source ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws/install/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1

ros2 run zed2_object_localization object_to_3d
```

An OpenCV window shows the detected object.

Example output:

```text
Object center (505, 188) -> X=-0.187 m, Y=-0.239 m, Z=0.971 m
```

The important difference compared with Example 01 is:

```text
Example 01
Fixed pixel
    ↓
3D coordinate

Example 02
Detected object
    ↓
Object center
    ↓
3D coordinate
```

---

# 7. Example 03 - Native ZED AI Object Detection

File:

```text
zed2_object_localization/step03_zed_object_detection.py
```

The third example replaces the simple classical detector with the native AI Object Detection provided by the ZED SDK and ZED ROS 2 Wrapper.

The pipeline becomes:

```text
ZED 2
   ↓
ZED SDK
   ↓
AI Object Detection
   ↓
zed_msgs/msg/ObjectsStamped
   ↓
Object Class
   ↓
2D Bounding Box
   ↓
3D Position
```

The ZED ROS 2 Wrapper publishes detected objects on:

```text
/zed/zed_node/obj_det/objects
```

The message type is:

```text
zed_msgs/msg/ObjectsStamped
```

Each detected object contains information including:

```text
label
label_id
sublabel
confidence
position
velocity
bounding_box_2d
bounding_box_3d
dimensions_3d
tracking_state
```

During the experiment, the ZED detector successfully recognized objects such as:

```text
Laptop
Person
```

## Example 03 - Terminal 1

Start the ZED 2 camera.

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1

ros2 launch zed_wrapper zed_camera.launch.py \
  camera_model:=zed2
```

Leave Terminal 1 running.

## Example 03 - Terminal 2

Enable the ZED Object Detection module.

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning/phase_05_ai_object_detection/ros2_ws

source /opt/ros/jazzy/setup.bash
source ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws/install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1

ros2 service call \
  /zed/zed_node/enable_obj_det \
  std_srvs/srv/SetBool \
  "{data: true}"
```

Successful response:

```text
success=True
message='Object Detection started'
```

If Object Detection is already active:

```text
success=False
message='Object Detection is already running'
```

This is not an error. It means the detector is already running.

## Example 03 - Terminal 3

Run our ZED AI Object Detection visualization node.

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning/phase_05_ai_object_detection/ros2_ws

source /opt/ros/jazzy/setup.bash
source ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws/install/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1

ros2 run zed2_object_localization zed_object_detection
```

The OpenCV visualization shows the AI-detected objects together with their bounding boxes and 3D information.

---

# 8. ZED ObjectsStamped Message

The ZED detector publishes:

```text
/zed/zed_node/obj_det/objects
```

with:

```text
zed_msgs/msg/ObjectsStamped
```

An example detected object was:

```yaml
label: ELECTRONICS
sublabel: Laptop
confidence: 23.935165405273438

position:
- 0.226863294839859
- -0.20143015682697296
- -0.0565602146089077
```

The message frame was:

```text
zed_left_camera_frame
```

This is important because the object coordinates are initially expressed relative to the ZED camera.

For robot manipulation, the coordinates must eventually be transformed into the robot coordinate system.

---

# 9. Example 04 - AI Object Position in Robot Base Frame

File:

```text
zed2_object_localization/step04_object_to_robot_frame.py
```

The final example combines:

```text
AI Object Detection
+
3D Object Position
+
TF2
```

The pipeline is:

```text
ZED AI Object Detection
        ↓
ObjectsStamped
        ↓
Object position
        ↓
zed_left_camera_frame
        ↓
TF2
        ↓
robot_base
```

This is the most important step for later robot manipulation.

A robot cannot directly use image coordinates.

It needs an object position relative to its own coordinate system.

---

# 10. Understanding the ZED TF Tree

The ZED ROS 2 Wrapper creates its own TF tree.

Relevant frames include:

```text
map
 ↓
odom
 ↓
zed_camera_link
 ↓
zed_camera_center
 ↓
zed_left_camera_frame
```

The relevant static ZED transforms observed during Phase 05 included:

```text
zed_camera_link
    ↓
zed_camera_center
    ↓
zed_left_camera_frame
```

For example:

```text
zed_camera_link -> zed_camera_center
Translation:
x = 0.000
y = 0.000
z = 0.015

Rotation:
pitch ≈ 2.865°
```

and:

```text
zed_camera_center -> zed_left_camera_frame

Translation:
x = -0.010
y =  0.060
z =  0.000
```

---

# 11. Important TF2 Lesson

Initially we tried to publish:

```text
robot_base
    ↓
zed_camera_link
```

using another static transform.

This caused disconnected or conflicting TF trees because the ZED ROS 2 Wrapper already manages the camera side of the TF hierarchy.

The working solution was to connect the robot coordinate system to the root of the existing ZED TF tree:

```text
robot_base
    ↓
map
    ↓
...
    ↓
zed_camera_link
    ↓
zed_camera_center
    ↓
zed_left_camera_frame
```

For this Phase 05 experiment we used the temporary example transform:

```text
robot_base -> map

translation:
x = 0.50 m
y = 0.00 m
z = 0.80 m

rotation:
roll  = 0
pitch = 0
yaw   = 0
```

These are demonstration values for the Phase 05 TF workflow.

They are not a real camera-to-robot calibration.

A real physical setup requires measured/calibrated extrinsic parameters.

---

# 12. Example 04 - Complete Five-Terminal Setup

This is the complete working terminal configuration used for the final Phase 05 example.

## Terminal 1 - Start ZED 2

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1

ros2 launch zed_wrapper zed_camera.launch.py \
  camera_model:=zed2
```

Leave Terminal 1 running.

---

## Terminal 2 - Enable ZED AI Object Detection

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning/phase_05_ai_object_detection/ros2_ws

source /opt/ros/jazzy/setup.bash
source ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws/install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1

ros2 service call \
  /zed/zed_node/enable_obj_det \
  std_srvs/srv/SetBool \
  "{data: true}"
```

Example response:

```text
response:
std_srvs.srv.SetBool_Response(
    success=True,
    message='Object Detection started'
)
```

If already running:

```text
success=False
message='Object Detection is already running'
```

---

## Terminal 3 - Connect Robot Base to ZED TF Tree

Publish the temporary Phase 05 transform:

```bash
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp

ros2 run tf2_ros static_transform_publisher \
  --x 0.50 \
  --y 0.00 \
  --z 0.80 \
  --roll 0.0 \
  --pitch 0.0 \
  --yaw 0.0 \
  --frame-id robot_base \
  --child-frame-id map
```

Leave Terminal 3 running.

Expected output:

```text
Spinning until stopped - publishing transform

translation:
('0.500000', '0.000000', '0.800000')

rotation:
('0.000000', '0.000000', '0.000000', '1.000000')

from 'robot_base' to 'map'
```

---

## Terminal 4 - Verify TF Chain

```bash
source /opt/ros/jazzy/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp

ros2 run tf2_ros tf2_echo \
  robot_base \
  zed_left_camera_frame
```

Once all TF publishers have been discovered, a valid transform must be displayed.

The important condition is:

```text
robot_base
    ↓
map
    ↓
ZED TF tree
    ↓
zed_left_camera_frame
```

Terminal 4 is useful for verifying that the complete coordinate system is connected before running the localization node.

---

## Terminal 5 - Transform AI Objects into Robot Base Frame

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning/phase_05_ai_object_detection/ros2_ws

source /opt/ros/jazzy/setup.bash
source ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws/install/setup.bash
source install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1

ros2 run zed2_object_localization object_to_robot_frame
```

At startup it reports:

```text
Object localization: zed_left_camera_frame -> robot_base
```

Immediately after startup, TF2 may briefly report that `robot_base` is not yet available while ROS 2 discovers the transient-local TF publishers.

Once the complete TF tree is available, object transformations start automatically.

---

# 13. Final Result

The final experiment successfully detected a laptop and a person.

Example laptop:

```text
Laptop

Camera frame:
x =  0.227 m
y = -0.173 m
z = -0.059 m

Robot base frame:
x =  0.607 m
y = -0.310 m
z =  0.640 m
```

Example person:

```text
Person

Camera frame:
x = 0.460 m
y = 0.380 m
z = -0.010 m

Robot base frame:
x = 0.807 m
y = 0.253 m
z = 0.717 m
```

The node therefore performs:

```text
ZED AI Detection
        ↓
Object Class
        ↓
3D Camera Coordinate
        ↓
TF2 Transformation
        ↓
3D Robot Coordinate
```

---

# 14. Phase 05 Programs

## Step 01

```text
step01_pixel_to_3d.py
```

Purpose:

```text
Pixel + Depth + Intrinsics
          ↓
         XYZ
```

This establishes the mathematical foundation of 3D perception.

---

## Step 02

```text
step02_object_to_3d.py
```

Purpose:

```text
Classical Object Detection
          ↓
Bounding Box Center
          ↓
Depth
          ↓
3D Object Position
```

This connects object detection with depth perception.

---

## Step 03

```text
step03_zed_object_detection.py
```

Purpose:

```text
ZED AI Object Detection
          ↓
ObjectsStamped
          ↓
AI Object Class
          ↓
3D Position
```

This replaces the simple detector with the native ZED AI perception pipeline.

---

## Step 04

```text
step04_object_to_robot_frame.py
```

Purpose:

```text
ZED Object Position
        ↓
zed_left_camera_frame
        ↓
TF2
        ↓
robot_base
```

This converts perception information into coordinates that can later be used by a robot.

---

# 15. What We Learned

Phase 05 connects several important robotics concepts:

```text
Computer Vision
     +
Depth Perception
     +
AI Object Detection
     +
Coordinate Frames
     +
TF2
     =
3D Object Localization
```

The progression was:

```text
Step 01
Pixel
 ↓
XYZ

Step 02
Object
 ↓
Bounding Box
 ↓
XYZ

Step 03
AI Object Detection
 ↓
Object Class
 ↓
XYZ

Step 04
AI Object
 ↓
Camera XYZ
 ↓
TF2
 ↓
Robot XYZ
```

This is the transition from basic perception to robot-usable perception.

---

# 16. Important Distinction - Detection vs Localization

Object Detection answers:

```text
What object is visible?
Where is it in the image?
```

3D Object Localization answers:

```text
Where is the object physically located in 3D space?
```

Robot-frame localization answers:

```text
Where is the detected object relative to the robot?
```

Therefore Phase 05 covers both:

```text
AI Object Detection
+
3D Object Localization
```

---

# 17. Temporary TF vs Real Calibration

The transform used in this phase:

```text
robot_base -> map

x = 0.50
y = 0.00
z = 0.80
```

was intentionally used to demonstrate and validate the complete TF2 transformation pipeline.

It is not a measured extrinsic calibration.

For a real OpenMANIPULATOR-X setup, the actual physical relationship between:

```text
robot_base
```

and:

```text
ZED 2
```

must be determined by measurement or calibration.

The final production pipeline will therefore become:

```text
Physical Robot
      ↓
Real robot_base
      ↓
Calibrated Camera Transform
      ↓
ZED 2
      ↓
AI Detection
      ↓
3D Object Position
      ↓
TF2
      ↓
Object Position in Robot Coordinates
```

---

# 18. Phase 05 Result

Phase 05 successfully demonstrated the complete progression:

```text
2D Image
   ↓
Depth
   ↓
3D Point
   ↓
Object Detection
   ↓
AI Object Detection
   ↓
3D AI Object Position
   ↓
TF2
   ↓
Robot Base Coordinate
```

The final system can identify an object such as a laptop or person, obtain its 3D position from the ZED 2 and transform that position into the `robot_base` coordinate frame.

This provides the perception foundation required for later robot manipulation and imitation-learning workflows.
