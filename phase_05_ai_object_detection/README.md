# Phase 05 - AI Object Detection

## ROS 2 Perception & Imitation Learning

Phase 05 extends the perception pipeline from the previous phases with real object detection and 3D object localization.

The goal is no longer to select an arbitrary image pixel manually.

Instead, the system detects real objects in the RGB image and determines their spatial position in 3D.

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
Object Center
  ↓
3D Object Position
  ↓
Camera Frame
  ↓
TF2
  ↓
Robot Base Frame
```

---

# 1. Phase 05 Goals

The goals of Phase 05 are:

- convert a 2D image pixel into a 3D point
- understand pixel + depth → XYZ
- detect objects in an RGB image
- use native ZED 2 object detection
- obtain the 3D position of detected objects
- understand the ZED object detection ROS 2 messages
- use TF2 to transform object coordinates between coordinate frames
- transform detected objects from the ZED camera frame into a robot base frame
- prepare the perception pipeline for later robot manipulation and imitation learning

---

# 2. Project Structure

The Phase 05 directory is:

```text
~/projects/robotics/ros2_perception_imitation_learning/phase_05_ai_object_detection
```

Structure:

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

The ROS 2 package is:

```text
zed2_object_localization
```

---

# 3. Prerequisites

The following components are used:

- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- ZED 2
- ZED SDK
- ZED ROS 2 Wrapper
- OpenCV
- cv_bridge
- TF2
- Python 3

The ZED ROS 2 workspace from Phase 01 is reused:

```text
~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws
```

The Phase 05 workspace is:

```text
~/projects/robotics/ros2_perception_imitation_learning/phase_05_ai_object_detection/ros2_ws
```

---

# 4. ROS 2 Environment

For all ROS 2 terminals in this phase:

```bash
source /opt/ros/jazzy/setup.bash

source ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws/install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1
```

For Phase 05 nodes additionally source:

```bash
source ~/projects/robotics/ros2_perception_imitation_learning/phase_05_ai_object_detection/ros2_ws/install/setup.bash
```

---

# 5. Step 01 - Pixel to 3D

File:

```text
zed2_object_localization/step01_pixel_to_3d.py
```

The first step demonstrates the fundamental relationship between:

```text
RGB Pixel
   +
Depth
   ↓
3D Position
```

An image pixel is represented by:

```text
u, v
```

Using the corresponding depth information, the 3D position can be determined:

```text
X
Y
Z
```

This establishes the fundamental connection between 2D and 3D perception.

---

# 6. Step 02 - Object to 3D

File:

```text
zed2_object_localization/step02_object_to_3d.py
```

The next step combines object detection with depth information.

The processing pipeline is:

```text
RGB Image
   ↓
Object Detection
   ↓
2D Bounding Box
   ↓
Bounding Box Center
   ↓
Depth / Point Cloud
   ↓
3D Object Position
```

The fundamental concept is:

```text
Object Detection
+
Depth
=
3D Object Localization
```

At this stage, the object position is expressed relative to the camera coordinate system.

---

# 7. Step 03 - Native ZED Object Detection

File:

```text
zed2_object_localization/step03_zed_object_detection.py
```

The ZED 2 native object detection pipeline is used to detect objects and obtain their 3D information.

Object detection is enabled through the ZED ROS 2 service:

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

If object detection is already active:

```text
success=False
message='Object Detection is already running'
```

This does not indicate a failure of the running detector. It means that object detection has already been enabled.

---

# 8. ZED Object Detection Topic

Detected objects are published on:

```text
/zed/zed_node/obj_det/objects
```

The topic type is:

```text
zed_msgs/msg/ObjectsStamped
```

The interface can be inspected with:

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning/phase_05_ai_object_detection/ros2_ws

source /opt/ros/jazzy/setup.bash
source ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws/install/setup.bash

export ROS_DOMAIN_ID=30
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONNOUSERSITE=1

ros2 topic type /zed/zed_node/obj_det/objects

TYPE=$(ros2 topic type /zed/zed_node/obj_det/objects)
ros2 interface show "$TYPE"

timeout 10 ros2 topic echo \
  /zed/zed_node/obj_det/objects \
  --once
```

---

# 9. ZED Object Message

The message contains an array of detected objects.

Important fields include:

```text
label
label_id
sublabel
confidence
position
position_covariance
velocity
tracking_available
tracking_state
action_state
bounding_box_2d
bounding_box_3d
dimensions_3d
```

The most important field for 3D localization is:

```text
float32[3] position
```

A detected object can therefore directly provide:

```text
X
Y
Z
```

Example from the experiment:

```text
label: ELECTRONICS
sublabel: Laptop

position:
  X ≈ 0.227 m
  Y ≈ -0.201 m
  Z ≈ -0.057 m
```

The ZED pipeline therefore combines:

```text
Object Detection
+
Stereo Depth
+
3D Localization
```

---

# 10. Native ZED Object Detection Visualization

The visualization created in:

```text
step03_zed_object_detection.py
```

shows detected objects directly in the ZED RGB image.

The visualization contains:

- object label
- confidence
- 2D bounding box
- object center
- X coordinate
- Y coordinate
- Z coordinate

Objects successfully detected during the experiment included:

```text
Person
Laptop
```

The resulting pipeline is:

```text
ZED 2
  ↓
RGB Image
  ↓
Native Object Detection
  ↓
Bounding Box
  ↓
Object Position X/Y/Z
```

---

# 11. Why Camera Coordinates Are Not Enough

The ZED detector initially reports the detected object's position in the camera coordinate system.

Example:

```text
Laptop

camera:
X ≈ 0.227 m
Y ≈ -0.173 m
Z ≈ -0.059 m
```

For robot manipulation this is not sufficient.

A robot normally needs the position relative to its own base frame:

```text
Object Position
      ↓
Robot Base Frame
```

Therefore the coordinate position must be transformed using TF2.

---

# 12. Step 04 - Object to Robot Frame

File:

```text
zed2_object_localization/step04_object_to_robot_frame.py
```

This node subscribes to:

```text
/zed/zed_node/obj_det/objects
```

and transforms the detected 3D object positions using TF2.

The goal is:

```text
Object Position
      ↓
Camera Frame
      ↓
TF2
      ↓
Robot Base Frame
```

The source frame reported by the ZED object message is:

```text
zed_left_camera_frame
```

The target frame used by the Phase 05 node is:

```text
robot_base
```

---

# 13. ZED TF Frames

The ZED wrapper publishes its own TF hierarchy.

Important frames observed during the experiment include:

```text
map
zed_camera_link
zed_camera_center
zed_left_camera_frame
zed_left_camera_frame_optical
zed_right_camera_frame
zed_right_camera_frame_optical
```

The internal ZED static hierarchy includes:

```text
zed_camera_link
      ↓
zed_camera_center
      ↓
zed_left_camera_frame
```

The transformation between:

```text
zed_camera_link
```

and:

```text
zed_left_camera_frame
```

was successfully verified.

Example:

```text
Translation:
X = -0.010 m
Y =  0.060 m
Z =  0.015 m

Rotation:
Pitch ≈ 2.865°
```

---

# 14. TF2 Problem Encountered

Initially the experimental robot frame was connected directly to:

```text
zed_camera_link
```

using:

```text
robot_base
   ↓
zed_camera_link
```

The static transform itself appeared correctly on:

```text
/tf_static
```

but TF2 still reported:

```text
Could not find a connection between 'robot_base'
and 'zed_left_camera_frame'
because they are not part of the same tree.

Tf has two or more unconnected trees.
```

Inspection of `/tf_static` showed that the static transform publisher was active, while the ZED wrapper maintained its own TF hierarchy.

The important lesson from this experiment is:

```text
Seeing a transform on /tf_static does not automatically
guarantee that the complete TF graph used by the application
forms the intended connected tree.
```

The existing sensor TF hierarchy therefore has to be inspected before adding an external robot frame.

---

# 15. Working TF Connection

For the current experiment, the working connection was created between:

```text
robot_base
```

and the ZED global frame:

```text
map
```

The resulting hierarchy was:

```text
robot_base
    ↓
   map
    ↓
ZED TF Tree
    ↓
zed_left_camera_frame
```

The experimental static transform was started with:

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

The values:

```text
X = 0.50 m
Y = 0.00 m
Z = 0.80 m
```

are experimental values only.

They are not yet a calibrated camera-to-robot extrinsic transformation.

For a real robot setup, this transformation must be determined from the actual physical camera mounting or through calibration.

---

# 16. Successful TF2 Transformation

After connecting `robot_base` to the existing ZED TF hierarchy, TF2 successfully calculated the complete transformation.

Example observed during the experiment:

```text
robot_base → zed_left_camera_frame

Translation:
X ≈ 0.370 m
Y ≈ -0.153 m
Z ≈ 0.711 m
```

The values changed slightly over time because ZED positional tracking was active.

---

# 17. Successful Object Transformation

The Phase 05 node successfully transformed detected objects from the ZED camera frame into `robot_base`.

Example:

```text
Laptop

camera:
(0.227, -0.173, -0.059) m

robot_base:
(0.607, -0.310, 0.640) m
```

Another detected object:

```text
Person

camera:
(0.460, 0.380, -0.010) m

robot_base:
(0.807, 0.253, 0.717) m
```

The complete transformation is therefore:

```text
Detected Object
      ↓
3D Camera Coordinates
      ↓
TF2
      ↓
Robot Base Coordinates
```

---

# 18. Complete Phase 05 Architecture

The completed Phase 05 architecture is:

```text
                         ZED 2
                           │
                           ▼
                       RGB Image
                           │
                           ▼
                  ZED Object Detection
                           │
                           ▼
                    2D Bounding Box
                           │
                           ▼
                 Stereo Depth / 3D Data
                           │
                           ▼
                  3D Object Position
                           │
                           ▼
               zed_left_camera_frame
                           │
                           ▼
                          TF2
                           │
                           ▼
                         map
                           │
                           ▼
                      robot_base
                           │
                           ▼
             Robot-relative Object Position
```

---

# 19. ROS 2 Interfaces Used

## Object Detection Topic

```text
/zed/zed_node/obj_det/objects
```

Message type:

```text
zed_msgs/msg/ObjectsStamped
```

## Object Detection Service

```text
/zed/zed_node/enable_obj_det
```

Service type:

```text
std_srvs/srv/SetBool
```

## TF Topics

```text
/tf
/tf_static
```

---

# 20. ROS 2 Package Files

The Python package contains:

```text
step01_pixel_to_3d.py
step02_object_to_3d.py
step03_zed_object_detection.py
step04_object_to_robot_frame.py
```

The corresponding ROS 2 console scripts are:

```text
pixel_to_3d
object_to_3d
zed_object_detection
object_to_robot_frame
```

---

# 21. Build Phase 05

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

source install/setup.bash
```

---

# 22. Run Object Detection

With the ZED ROS 2 node already running:

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

---

# 23. Run Robot Frame Connection

In a separate terminal:

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

This terminal must remain running while the experimental transform is required.

---

# 24. Run Object-to-Robot Transformation

In another terminal:

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

Expected output:

```text
Object localization: zed_left_camera_frame -> robot_base

Laptop | camera=(...) m | robot_base=(...) m
Person | camera=(...) m | robot_base=(...) m
```

---

# 25. What We Learned

Phase 05 combines several important robotics perception concepts.

## 2D Perception

```text
RGB Image
→ Object Detection
→ Bounding Box
```

## 3D Perception

```text
Bounding Box
+
Stereo Depth
→ 3D Object Position
```

## Coordinate Transformation

```text
Camera Coordinates
→ TF2
→ Robot Coordinates
```

## Complete Robotics Perception Chain

```text
Camera
→ Perception
→ Object Detection
→ 3D Position
→ Coordinate Transformation
→ Robot Frame
```

A robot cannot use only the pixel position of an object.

For manipulation it needs to determine:

```text
What is the object?

Where is the object in 3D?

Where is the object relative to the robot?
```

Phase 05 demonstrates all three steps.

---

# 26. Phase 05 Status

Completed:

- [x] Pixel to 3D
- [x] Pixel + depth → XYZ
- [x] Object detection
- [x] Native ZED object detection
- [x] ZED object detection ROS 2 messages
- [x] 2D bounding boxes
- [x] 3D bounding boxes
- [x] Object confidence
- [x] Object 3D position
- [x] Native ZED detection visualization
- [x] ZED TF tree analysis
- [x] Camera-frame coordinates
- [x] TF2 coordinate transformation
- [x] Robot-base coordinates
- [x] Complete object localization pipeline

Phase 05 therefore establishes:

```text
Object Detection
+
3D Perception
+
TF2
=
Robot-relative 3D Object Localization
```

---

# 27. Important Limitation

The current transform between:

```text
robot_base
```

and:

```text
map
```

uses experimental values:

```text
X = 0.50 m
Y = 0.00 m
Z = 0.80 m
Roll  = 0.0
Pitch = 0.0
Yaw   = 0.0
```

These values demonstrate the TF2 pipeline but do not yet represent a physically calibrated camera-to-robot relationship.

Before using the coordinates for real robot manipulation, the camera pose relative to the robot must be measured or calibrated.

---

# 28. Next Phase

The next project phase is:

```text
phase_06_segmentation
```

The perception pipeline will progress from:

```text
Object Detection
↓
Bounding Box
```

toward:

```text
Image Segmentation
↓
Pixel-level Object Mask
```

This provides more precise object geometry and prepares the perception system for later robot manipulation, dataset recording and imitation learning.
