**# Phase 01 – Camera & ROS 2 Validation**

**## ROS 2 Perception & Imitation Learning**

Phase 01 validates the complete camera and ROS 2 foundation for the project.

The two cameras tested are:

- Stereolabs ZED 2

- Intel RealSense D435i

Both cameras are validated before starting the actual perception pipeline.

The goal is to verify:

- Camera hardware

- USB connectivity

- Camera SDK

- ROS 2 integration

- RGB streams

- Depth streams

- 3D PointCloud

- IMU

- TF / Extrinsics

- Camera stability

After this phase, the project can continue with 2D perception, 3D perception, AI object detection, segmentation, robot manipulation, dataset recording and imitation learning.

**---**

**# 1. Project Directory**

Main project:

```text

~/projects/robotics/ros2_perception_imitation_learning

```

Phase 01:

```text

~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2

```

Structure:

```text

phase_01_camera_ros2/

├── zed2/

│   └── ros2_ws/

└── realsense_d435i/

```

Complete project structure:

```text

ros2_perception_imitation_learning/

├── phase_01_camera_ros2/

│   ├── zed2/

│   └── realsense_d435i/

├── phase_02_2d_perception/

├── phase_03_3d_perception/

├── phase_04_tf2_calibration/

├── phase_05_ai_object_detection/

├── phase_06_segmentation/

├── phase_07_isaac_ros/

├── phase_08_foundationpose/

├── phase_09_robot_manipulation/

├── phase_10_dataset_recording/

├── phase_11_pytorch_imitation_learning/

├── phase_12_policy_robot/

├── phase_13_isaac_lab_mimic/

└── phase_14_groot_sim_to_real/

```

**---**

**# 2. Overall Architecture**

```text

                     CAMERA LAYER

                          │

             ┌────────────┴────────────┐

             │                         │

          ZED 2                 RealSense D435i

             │                         │

      Stereolabs SDK              librealsense

             │                         │

    zed-ros2-wrapper          realsense2_camera

             │                         │

             └────────────┬────────────┘

                          │

                     ROS 2 Jazzy

                          │

        ┌─────────────────┼─────────────────┐

        │                 │                 │

       RGB              Depth              IMU

        │                 │                 │

        │                 └───────┐         │

        │                         │         │

        └─────────────────┬───────┴─────────┘

                          │

                     Point Cloud

                          │

                         TF2

                          │

                          ▼

                   2D Perception

                          │

                   3D Perception

                          │

                 AI Object Detection

                          │

                    Segmentation

                          │

                   Object 6D Pose

                          │

                  Robot Manipulation

                          │

                  Dataset Recording

                          │

               PyTorch Imitation Learning

                          │

                    Robot Policy

                          │

                  Isaac Lab Mimic

                          │

                   GR00T / Sim-to-Real

```

**---**

**# 3. Camera Roles**

**## ZED 2**

Main role:

```text

ZED 2

 ↓

ROS 2

 ↓

Perception

 ↓

2D + 3D Vision

 ↓

AI Perception

 ↓

TurtleBot3 / mobile perception

```

The ZED 2 is the primary perception-development camera.

Important capabilities:

- Stereo vision

- RGB

- Depth

- PointCloud

- IMU

- Positional tracking

- Odometry

- AI models

- NVIDIA GPU acceleration

- NITROS support

**---**

**## Intel RealSense D435i**

Main role:

```text

D435i

 ↓

ROS 2

 ↓

RGB-D Perception

 ↓

Manipulation

 ↓

OpenMANIPULATOR-X

 ↓

Dataset Recording

 ↓

Imitation Learning

```

The D435i is particularly useful for the manipulator because it is considerably smaller and lighter than the ZED 2.

Important capabilities:

- RGB

- Stereo Depth

- Infrared

- PointCloud

- Gyroscope

- Accelerometer

- Depth-to-Color alignment

- Compact form factor

The exact final camera/robot assignment can still evolve in later phases.

**---**

**# 4. System Requirements**

Development system used for this phase:

```text

OS:

Ubuntu 24.04.4 LTS

ROS:

ROS 2 Jazzy

GPU:

NVIDIA GeForce RTX 5090 Laptop GPU

VRAM:

~24 GB

NVIDIA Driver:

595.84

CUDA Driver:

13.2

```

General software requirements:

```text

ROS 2 Jazzy

Python 3

Git

colcon

rosdep

CMake

NVIDIA Driver

CUDA

```

**---**

**# 5. ZED 2 Requirements**

Validated environment:

```text

Camera:

Stereolabs ZED 2

ZED SDK:

5.4.1

ROS:

ROS 2 Jazzy

ZED ROS Wrapper:

zed-ros2-wrapper

GPU:

NVIDIA RTX 5090 Laptop GPU

CUDA:

Working

Connection:

USB 3.x SuperSpeed

```

Repository:

```text

https://github.com/stereolabs/zed-ros2-wrapper

```

**---**



**---**

**# 5A. Fresh Installation – ZED SDK on Ubuntu 24.04**

The existing Phase 01 system already had ZED SDK 5.4.1 installed.
For a fresh Ubuntu 24.04 system, install the ZED SDK before building the ROS 2 wrapper.

Official documentation:

```text
https://docs.stereolabs.com/docs/development/zed-sdk/linux
```

Download the ZED SDK installer that matches Ubuntu 24.04 and the installed CUDA version from the official Stereolabs download page.

Go to the download directory:

```bash
cd ~/Downloads
```

Install `zstd` if required:

```bash
sudo apt update
sudo apt install zstd
```

Make the downloaded installer executable. Replace the placeholder with the actual downloaded file name:

```bash
chmod +x ZED_SDK_UbuntuXX_cudaYY.Y_vZ.Z.Z.zstd.run
```

Run the installer:

```bash
./ZED_SDK_UbuntuXX_cudaYY.Y_vZ.Z.Z.zstd.run
```

After installation verify:

```bash
ls -ld /usr/local/zed
/usr/local/zed/tools/ZED_Explorer --version
/usr/local/zed/tools/ZED_Diagnostic
```

For this project the validated installed version was:

```text
ZED SDK 5.4.1
```


**# 6. ZED 2 – Initial Hardware Test**

Directory:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2

```

Check USB:

```bash

lsusb | grep -i -E 'stereo|zed|2b03'

```

Detected devices:

```text

STEREOLABS ZED 2

STEREOLABS ZED-2 HID INTERFACE

```

Check USB topology:

```bash

lsusb -t

```

The main ZED 2 video interface was detected at:

```text

5000M

```

This confirms SuperSpeed operation.

The ZED HID/IMU interface appears separately on the USB 2.x tree.

**---**

**# 7. ROS 2 Validation**

```bash

echo "ROS_DISTRO=$ROS_DISTRO"

which ros2

ros2 --help >/dev/null 2>&1 && \\

echo "ROS 2: OK" || \\

echo "ROS 2: NOT FOUND"

```

Result:

```text

ROS_DISTRO=jazzy

/opt/ros/jazzy/bin/ros2

ROS 2: OK

```

**---**

**# 8. ZED SDK Validation**

Check SDK installation:

```bash

ls -ld /usr/local/zed

```

Result:

```text

/usr/local/zed

```

Installed ZED tools included:

```text

ZED360

ZED_Calibration

ZED_Depth_Viewer

ZED_Diagnostic

ZED_Explorer

ZED_Sensor_Placer

ZED_Sensor_Viewer

ZED_Studio

ZED_SVO_Editor

ZEDfu

```

ZED SDK version:

```text

5.4.1

```

**---**

**# 9. ZED Diagnostic Results**

ZED Diagnostic confirmed:

```text

Camera:

ZED 2

USB Bandwidth:

OK

GPU:

NVIDIA GeForce RTX 5090 Laptop GPU

CUDA Operations:

Working correctly

Compute Capability:

12.0

GPU Memory:

~24 GB

ZED SDK:

5.4.1

```

Available ZED AI models included:

```text

MULTI CLASS DETECTION

MULTI CLASS MEDIUM DETECTION

MULTI CLASS ACCURATE DETECTION

HUMAN BODY FAST DETECTION

HUMAN BODY MEDIUM DETECTION

HUMAN BODY ACCURATE DETECTION

HUMAN BODY 38 FAST DETECTION

HUMAN BODY 38 MEDIUM DETECTION

HUMAN BODY 38 ACCURATE DETECTION

PERSON HEAD DETECTION

PERSON HEAD ACCURATE DETECTION

REID ASSOCIATION

NEURAL LIGHT DEPTH

NEURAL DEPTH

NEURAL PLUS DEPTH

```

These models can become relevant during later AI perception phases.

**---**

**# 10. ZED ROS 2 Workspace**

Create workspace:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2

mkdir -p ros2_ws/src

cd ros2_ws/src

```

Clone wrapper:

```bash

git clone https://github.com/stereolabs/zed-ros2-wrapper.git

```

Install dependencies:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash

rosdep install \\

  --from-paths src \\

  --ignore-src \\

  -r \\

  -y

```

Result:

```text

All required rosdeps installed successfully

```

**---**



**---**

**# 10A. ZED Wrapper as Git Submodule**

The ZED ROS 2 Wrapper is an external Stereolabs repository and is therefore not copied into this repository as ordinary project source code.
It is tracked as a Git submodule at:

```text
phase_01_camera_ros2/zed2/ros2_ws/src/zed-ros2-wrapper
```

For a fresh clone of this project including the wrapper:

```bash
cd ~/projects/robotics

git clone --recurse-submodules \
  https://github.com/vagotec/ros2_perception_imitation_learning.git
```

If the project was cloned without submodules:

```bash
cd ~/projects/robotics/ros2_perception_imitation_learning

git submodule update --init --recursive
```

Verify the submodule:

```bash
git submodule status
```

Validated submodule state during Phase 01:

```text
33dfefa07087281d309f9ddf471ab804a3e8474c
zed-ros2-wrapper
(v5.4.1-3-g33dfefa)
```

ROS 2 generated directories are local build artifacts and must not be committed:

```text
ros2_ws/build/
ros2_ws/install/
ros2_ws/log/
```

The project `.gitignore` therefore contains rules equivalent to:

```gitignore
**/build/
**/install/
**/log/
```

Only `src/` and project-authored source/configuration files belong in Git.


**# 11. Build ZED ROS 2 Wrapper**

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash

colcon build \\

  --symlink-install \\

  --cmake-args=-DCMAKE_BUILD_TYPE=Release \\

  --parallel-workers $(nproc)

```

Build result:

```text

zed_components    PASS

zed_wrapper       PASS

zed_debug         PASS

zed_ros2          PASS

```

Final build:

```text

Summary: 4 packages finished

```

NITROS support was detected during the build.

**---**

**# 12. Start ZED 2 with ROS 2**

Terminal 1:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash

source install/setup.bash

ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zed2

```

Successful startup:

```text

=== zed started ===

```

**---**

**# 13. ZED ROS 2 Topics**

Terminal 2:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash

source install/setup.bash

echo "=== ZED TOPICS ==="

ros2 topic list | grep zed

echo

echo "=== IMAGE TOPICS ==="

ros2 topic list | grep -E 'image|rgb'

echo

echo "=== DEPTH TOPICS ==="

ros2 topic list | grep depth

echo

echo "=== POINT CLOUD TOPICS ==="

ros2 topic list | grep -E 'point_cloud|pointcloud'

echo

echo "=== IMU TOPICS ==="

ros2 topic list | grep imu

```

Important validated topics:

```text

/zed/zed_node/rgb/color/rect/image

/zed/zed_node/depth/depth_registered

/zed/zed_node/point_cloud/cloud_registered

/zed/zed_node/imu/data

/zed/zed_node/odom

/zed/zed_node/pose

/zed/zed_node/pose/status

```

NITROS topics:

```text

/zed/zed_node/rgb/color/rect/image/nitros

/zed/zed_node/depth/depth_registered/nitros

```

**---**

**# 14. ZED Data Rate Test**

Terminal 2:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash

source install/setup.bash

echo "=== RGB RATE ==="

timeout 6 ros2 topic hz /zed/zed_node/rgb/color/rect/image

echo

echo "=== DEPTH RATE ==="

timeout 6 ros2 topic hz /zed/zed_node/depth/depth_registered

echo

echo "=== POINT CLOUD RATE ==="

timeout 6 ros2 topic hz /zed/zed_node/point_cloud/cloud_registered

echo

echo "=== IMU RATE ==="

timeout 6 ros2 topic hz /zed/zed_node/imu/data

```

Measured values:

```text

RGB:

~25–27 Hz

PointCloud:

~10 Hz

IMU:

~99 Hz

```

The initial `ros2 topic hz` command did not display a value for the Depth stream, so Depth was validated separately.

**---**

**# 15. ZED Depth Validation**

Check publisher:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash

source install/setup.bash

ros2 topic info \\

  /zed/zed_node/depth/depth_registered \\

  --verbose

```

Result:

```text

Type:

sensor_msgs/msg/Image

Publisher count:

1

Reliability:

RELIABLE

History:

KEEP_LAST (10)

Durability:

VOLATILE

```

Validate actual depth message:

```bash

timeout 10 ros2 topic echo \\

  /zed/zed_node/depth/depth_registered \\

  --qos-reliability reliable \\

  --once

```

Result:

```text

frame_id:

zed_left_camera_frame_optical

height:

720

width:

1280

encoding:

32FC1

```

`32FC1` means:

```text

32-bit floating point

1 channel

```

This confirms that real Depth data is being published.

**---**

**# 16. ZED Positional Tracking**

The ZED wrapper successfully started positional tracking.

Validated topics:

```text

/zed/zed_node/pose

/zed/zed_node/pose/status

/zed/zed_node/odom

```

Camera-to-IMU transformations were also initialized.

During startup the following warning appeared:

```text

Gravity alignment issues detected. Recomputing alignment...

```

The warning did not prevent camera startup or ROS 2 data publication.

**---**

**# 17. ZED USB / Mouse Investigation**

During one early test, the wireless mouse and keyboard temporarily became slow while the ZED 2 was connected.

Useful diagnostics:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2

echo "=== USB TREE ==="

lsusb -t

echo

echo "=== USB DEVICES ==="

lsusb

echo

echo "=== CPU / LOAD ==="

uptime

ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -20

echo

echo "=== MEMORY ==="

free -h

echo

echo "=== NVIDIA GPU ==="

nvidia-smi

echo

echo "=== RECENT USB / HID KERNEL MESSAGES ==="

sudo dmesg --ctime | grep -iE \\

'usb|xhci|hid|mouse|keyboard' | tail -80

```

The kernel log showed repeated resets of the ZED HID interface:

```text

reset full-speed USB device ... using xhci_hcd

```

USB topology showed:

```text

ZED video:

USB SuperSpeed / Bus 004 / 5000M

ZED HID:

USB 2.x tree / Bus 003

Logitech wireless receiver:

USB 2.x tree / Bus 003

```

After restarting the camera and ROS 2 node, the problem was no longer reproducible.

A later test showed:

```text

ZED connected:

Mouse normal

ZED ROS node running:

Mouse normal

```

Therefore no system configuration changes were made.

If the issue reappears, check:

```bash

lsusb -t

```

and:

```bash

sudo dmesg --ctime | grep -iE \\

'usb|xhci|hid|mouse|keyboard' | tail -100

```

before changing any configuration.

**---**

**# 18. ZED 2 Final Validation**

```text

Hardware                 PASS

USB detection            PASS

USB SuperSpeed           PASS

ZED SDK 5.4.1            PASS

CUDA                      PASS

RTX 5090                  PASS

ROS 2 Jazzy              PASS

ZED ROS Wrapper           PASS

RGB                       PASS

Depth                     PASS

PointCloud                PASS

IMU                       PASS

Pose                      PASS

Odometry                  PASS

TF / Camera transforms    PASS

NITROS                    PASS

```

ZED 2 is ready for perception development.

**---**

**# 19. RealSense D435i Requirements**

Validated environment:

```text

Camera:

Intel RealSense D435i

librealsense:

2.58.1

RealSense ROS:

4.58.1

Firmware:

5.17.0.10

USB:

3.2

ROS:

ROS 2 Jazzy

IMU:

BMI055

```

Installed ROS packages:

```text

realsense2_camera

realsense2_camera_msgs

realsense2_description

```

**---**



**---**

**# 19A. Fresh Installation – RealSense SDK and ROS 2 Packages**

The Phase 01 machine already had librealsense 2.58.1 and RealSense ROS 4.58.1 installed.
For a fresh Ubuntu 24.04 + ROS 2 Jazzy system, install the RealSense software stack before running the tests below.

Official librealsense documentation:

```text
https://github.com/realsenseai/librealsense
```

Ubuntu 24.04 is supported by current librealsense releases.

## Install librealsense from the RealSense APT repository

Create a keyring directory:

```bash
sudo mkdir -p /etc/apt/keyrings
```

Download and register the current RealSense repository key:

```bash
curl -sSf https://librealsense.realsenseai.com/Debian/librealsenseai.asc | \
  gpg --dearmor | \
  sudo tee /etc/apt/keyrings/librealsenseai.gpg > /dev/null
```

Install HTTPS repository support:

```bash
sudo apt update
sudo apt install apt-transport-https
```

Add the RealSense repository:

```bash
echo "deb [signed-by=/etc/apt/keyrings/librealsenseai.gpg] https://librealsense.realsenseai.com/Debian/apt-repo $(lsb_release -cs) main" | \
  sudo tee /etc/apt/sources.list.d/librealsense.list
```

Update package metadata:

```bash
sudo apt update
```

Install the runtime, kernel module integration and tools:

```bash
sudo apt install \
  librealsense2-dkms \
  librealsense2-utils
```

Optional development package:

```bash
sudo apt install librealsense2-dev
```

Reconnect the D435i after installation and verify:

```bash
realsense-viewer --version
rs-enumerate-devices --version
rs-enumerate-devices
```

## Install RealSense ROS 2 packages for Jazzy

```bash
source /opt/ros/jazzy/setup.bash

sudo apt update
sudo apt install \
  ros-jazzy-realsense2-camera \
  ros-jazzy-realsense2-camera-msgs \
  ros-jazzy-realsense2-description
```

Verify the packages:

```bash
ros2 pkg list | grep -i realsense
```

Expected packages:

```text
realsense2_camera
realsense2_camera_msgs
realsense2_description
```

The project uses the installed RealSense ROS 2 packages.
Unlike the ZED wrapper, no RealSense source repository was cloned into the project during Phase 01.


**# 20. RealSense Hardware Detection**

Directory:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/realsense_d435i

```

USB test:

```bash

lsusb | grep -i -E 'Intel|RealSense|8086'

```

Detected:

```text

Intel(R) RealSense(TM) Depth Camera 435i

```

USB ID:

```text

8086:0b3a

```

**---**

**# 21. RealSense SDK Tools**

Check:

```bash

command -v realsense-viewer

command -v rs-enumerate-devices

```

Installed:

```text

/opt/ros/jazzy/bin/realsense-viewer

/opt/ros/jazzy/bin/rs-enumerate-devices

```

Check versions:

```bash

realsense-viewer --version

rs-enumerate-devices --version

```

Result:

```text

2.58.1.0

```

**---**

**# 22. RealSense Device Information**

```bash

rs-enumerate-devices

```

Validated:

```text

Name:

Intel RealSense D435I

Firmware:

5.17.0.10

Product ID:

0B3A

Product Line:

D400

USB Type Descriptor:

3.2

Connection:

USB

IMU:

BMI055

```

**---**

**# 23. RealSense Supported Streams**

Depth examples:

```text

1280x720 Z16 @ 30/15/6 Hz

848x480 Z16 @ 90/60/30/15/6 Hz

640x480 Z16 @ 90/60/30/15/6 Hz

```

Color examples:

```text

1920x1080 @ 30/15/6 Hz

1280x720 @ 30/15/6 Hz

960x540 @ 60/30/15/6 Hz

848x480 @ 60/30/15/6 Hz

```

Motion module:

```text

Accelerometer:

250 / 63 Hz

Gyroscope:

400 / 200 Hz

```

**---**

**# 24. RealSense USB Validation**

Check topology:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/realsense_d435i

lsusb -t

```

Validated:

```text

USB 3.2

5000M

```

The D435i was connected to the SuperSpeed USB bus.

Mouse and keyboard remained on the USB 2.x bus.

This provides useful separation between the high-bandwidth RGB-D camera stream and wireless HID devices.

**---**

**# 25. RealSense Viewer**

Start:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/realsense_d435i

realsense-viewer

```

The RealSense Viewer successfully displayed camera data including a 3D PointCloud.

During one viewer test the following notification appeared:

```text

Right MIPI error

```

The camera was subsequently tested using ROS 2.

RGB, Depth, aligned Depth, PointCloud, Gyro and Accel all worked.

Therefore the message is currently treated as something to monitor rather than a blocking failure.

If it reappears repeatedly, USB/camera diagnostics should be performed.

**---**

**# 26. RealSense Diagnostic Commands**

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/realsense_d435i

echo "=== REALSENSE USB CONNECTION ==="

lsusb -t

echo

echo "=== REALSENSE DEVICE / FW ==="

rs-enumerate-devices | grep -E \\

'Name|Serial Number|Firmware Version|Usb Type Descriptor|Physical Port'

echo

echo "=== RECENT REALSENSE / USB KERNEL MESSAGES ==="

sudo dmesg --ctime | grep -iE \\

'realsense|8086|0b3a|usb|uvc|xhci' | tail -100

```

**---**

**# 27. RealSense ROS 2 Packages**

Check:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/realsense_d435i

source /opt/ros/jazzy/setup.bash

ros2 pkg list | grep -i realsense

```

Result:

```text

realsense2_camera

realsense2_camera_msgs

realsense2_description

```

No additional installation was necessary.

**---**

**# 28. Start RealSense ROS 2**

Terminal 1:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/realsense_d435i

source /opt/ros/jazzy/setup.bash

ros2 launch realsense2_camera rs_launch.py \\

  enable_color:=true \\

  enable_depth:=true \\

  enable_gyro:=true \\

  enable_accel:=true \\

  align_depth.enable:=true \\

  pointcloud.enable:=true

```

Successful startup:

```text

RealSense Node Is Up!

```

Detected:

```text

RealSense ROS:

4.58.1

Built with LibRealSense:

2.58.1

Running with LibRealSense:

2.58.1

USB:

3.2

Firmware:

5.17.0.10

```

**---**

**# 29. RealSense Runtime Profiles**

ROS 2 selected:

```text

Depth:

848x480

Z16

30 FPS

Color:

1280x720

RGB8

30 FPS

Gyro:

MOTION_XYZ32F

200 Hz

Accel:

MOTION_XYZ32F

63 Hz

```

**---**

**# 30. RealSense IMU Warning**

During startup:

```text

IMU Calibration is not available, default intrinsic and extrinsic will be used.

```

The Motion Module nevertheless started successfully.

Both streams were functional:

```text

Gyro:

200 Hz

Accel:

63 Hz

```

This warning does not block Phase 01.

It should be revisited later if high-precision visual-inertial fusion or calibration-sensitive applications are implemented.

**---**

**# 31. RealSense ROS 2 Topics**

Terminal 2:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/realsense_d435i

source /opt/ros/jazzy/setup.bash

echo "=== REALSENSE TOPICS ==="

ros2 topic list | grep camera

echo

echo "=== RGB TOPICS ==="

ros2 topic list | grep -E 'color.\*image|rgb'

echo

echo "=== DEPTH TOPICS ==="

ros2 topic list | grep depth

echo

echo "=== POINT CLOUD TOPICS ==="

ros2 topic list | grep -E 'pointcloud|points'

echo

echo "=== IMU TOPICS ==="

ros2 topic list | grep -E 'gyro|accel|imu'

```

Important topics:

```text

/camera/camera/color/image_raw

/camera/camera/color/camera_info

/camera/camera/depth/image_rect_raw

/camera/camera/depth/camera_info

/camera/camera/aligned_depth_to_color/image_raw

/camera/camera/aligned_depth_to_color/camera_info

/camera/camera/depth/color/points

/camera/camera/gyro/sample

/camera/camera/gyro/imu_info

/camera/camera/accel/sample

/camera/camera/accel/imu_info

```

Extrinsics:

```text

/camera/camera/extrinsics/depth_to_accel

/camera/camera/extrinsics/depth_to_color

/camera/camera/extrinsics/depth_to_gyro

```

**---**

**# 32. RealSense Data Rate Test**

Terminal 2:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/realsense_d435i

source /opt/ros/jazzy/setup.bash

echo "=== RGB RATE ==="

timeout 6 ros2 topic hz /camera/camera/color/image_raw

echo

echo "=== DEPTH RATE ==="

timeout 6 ros2 topic hz /camera/camera/depth/image_rect_raw

echo

echo "=== ALIGNED DEPTH RATE ==="

timeout 6 ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw

echo

echo "=== POINT CLOUD RATE ==="

timeout 6 ros2 topic hz /camera/camera/depth/color/points

echo

echo "=== GYRO RATE ==="

timeout 6 ros2 topic hz /camera/camera/gyro/sample

echo

echo "=== ACCEL RATE ==="

timeout 6 ros2 topic hz /camera/camera/accel/sample

```

Measured:

```text

RGB:

~29.9–30.0 Hz

Depth:

~30.0 Hz

Aligned Depth:

~29–30 Hz

Gyro:

~200.35 Hz

Accel:

~63.68 Hz

```

The initial PointCloud `ros2 topic hz` command did not display a rate.

Therefore the PointCloud itself was validated directly.

**---**

**# 33. RealSense PointCloud Validation**

Check publisher:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/realsense_d435i

source /opt/ros/jazzy/setup.bash

ros2 topic info \\

  /camera/camera/depth/color/points \\

  --verbose

```

Result:

```text

Type:

sensor_msgs/msg/PointCloud2

Publisher count:

1

Reliability:

RELIABLE

History:

KEEP_LAST (10)

Durability:

VOLATILE

```

Read one actual PointCloud:

```bash

timeout 10 ros2 topic echo \\

  /camera/camera/depth/color/points \\

  --once

```

Result:

```text

frame_id:

camera_depth_optical_frame

height:

1

width:

153373

```

Point fields:

```text

x

y

z

rgb

```

Therefore the D435i produces a valid colored 3D PointCloud.

**---**

**# 34. RealSense D435i Final Validation**

```text

Hardware                 PASS

USB detection            PASS

USB 3.2                   PASS

SuperSpeed                PASS

librealsense 2.58.1       PASS

Firmware 5.17.0.10        PASS

ROS 2 Jazzy              PASS

RealSense ROS 4.58.1      PASS

RGB                       PASS

Depth                     PASS

Aligned Depth             PASS

PointCloud                PASS

Gyroscope                 PASS

Accelerometer             PASS

Extrinsics                PASS

```

The D435i is ready for perception and manipulation development.

**---**

**# 35. Camera Comparison After Phase 01**

| Capability | ZED 2 | RealSense D435i |

|---|---|---|

| RGB | PASS | PASS |

| Stereo Depth | PASS | PASS |

| PointCloud | PASS | PASS |

| IMU | PASS | PASS |

| Gyroscope | PASS | PASS |

| Accelerometer | PASS | PASS |

| ROS 2 Jazzy | PASS | PASS |

| TF / Extrinsics | PASS | PASS |

| Positional Tracking | PASS | Not primary target |

| Odometry | PASS | Not primary target |

| NITROS | PASS | Not tested in Phase 01 |

| Integrated ZED AI Models | PASS | No equivalent tested |

| Compact Manipulator Mounting | Less suitable | Better suited |

| Mobile / 3D Perception | Primary role | Possible |

| OpenMANIPULATOR-X | Possible | Primary candidate |

| TurtleBot3 | Primary candidate | Possible |

**---**

**# 36. Important ROS 2 Message Types**

The following ROS 2 message types are important for the next phases.

RGB and Depth:

```text

sensor_msgs/msg/Image

```

Camera calibration:

```text

sensor_msgs/msg/CameraInfo

```

PointCloud:

```text

sensor_msgs/msg/PointCloud2

```

IMU:

```text

sensor_msgs/msg/Imu

```

Pose and transformations will later interact with:

```text

geometry_msgs

tf2

```

These message types form the basic interface between the camera layer and our own perception software.

**---**

**# 37. Perception Data Flow**

The important conceptual separation is:

```text

Camera

   │

   ▼

Camera SDK

   │

   ▼

ROS 2 Camera Driver

   │

   ├── RGB

   ├── Depth

   ├── PointCloud

   ├── CameraInfo

   └── IMU

        │

        ▼

Our ROS 2 Perception Nodes

        │

        ├── OpenCV

        ├── AI Models

        ├── 3D Processing

        ├── Object Detection

        └── Segmentation

```

Phase 01 therefore validates the input layer.

Starting with Phase 02, we begin writing our own perception software.

**---**

**# 38. Important Diagnostic Commands**

**## List cameras / USB devices**

```bash

lsusb

```

**## USB topology and speed**

```bash

lsusb -t

```

**## ROS 2 topics**

```bash

ros2 topic list

```

**## Topic information**

```bash

ros2 topic info <TOPIC> --verbose

```

Example:

```bash

ros2 topic info \\

  /camera/camera/depth/color/points \\

  --verbose

```

**## Read one message**

```bash

ros2 topic echo <TOPIC> --once

```

**## Measure frequency**

```bash

ros2 topic hz <TOPIC>

```

**## ROS nodes**

```bash

ros2 node list

```

**## ROS parameters**

```bash

ros2 param list

```

**## CPU load**

```bash

uptime

ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -20

```

**## Memory**

```bash

free -h

```

**## NVIDIA GPU**

```bash

nvidia-smi

```

**## USB kernel errors**

```bash

sudo dmesg --ctime | grep -iE \\

'usb|xhci|uvc|hid' | tail -100

```

**---**

**# 39. Quick Start – ZED 2**

Terminal 1:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash

source install/setup.bash

ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zed2

```

Terminal 2:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/zed2/ros2_ws

source /opt/ros/jazzy/setup.bash

source install/setup.bash

ros2 topic list | grep zed

```

RGB:

```bash

ros2 topic hz /zed/zed_node/rgb/color/rect/image

```

PointCloud:

```bash

ros2 topic hz /zed/zed_node/point_cloud/cloud_registered

```

IMU:

```bash

ros2 topic hz /zed/zed_node/imu/data

```

Depth sample:

```bash

ros2 topic echo \\

  /zed/zed_node/depth/depth_registered \\

  --qos-reliability reliable \\

  --once

```

**---**

**# 40. Quick Start – RealSense D435i**

Terminal 1:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/realsense_d435i

source /opt/ros/jazzy/setup.bash

ros2 launch realsense2_camera rs_launch.py \\

  enable_color:=true \\

  enable_depth:=true \\

  enable_gyro:=true \\

  enable_accel:=true \\

  align_depth.enable:=true \\

  pointcloud.enable:=true

```

Terminal 2:

```bash

cd ~/projects/robotics/ros2_perception_imitation_learning/phase_01_camera_ros2/realsense_d435i

source /opt/ros/jazzy/setup.bash

ros2 topic list | grep camera

```

RGB:

```bash

ros2 topic hz /camera/camera/color/image_raw

```

Depth:

```bash

ros2 topic hz /camera/camera/depth/image_rect_raw

```

Aligned Depth:

```bash

ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw

```

Gyro:

```bash

ros2 topic hz /camera/camera/gyro/sample

```

Accel:

```bash

ros2 topic hz /camera/camera/accel/sample

```

PointCloud sample:

```bash

ros2 topic echo \\

  /camera/camera/depth/color/points \\

  --once

```

**---**

**# 41. Phase 01 Result**

Both cameras are now successfully integrated into ROS 2 Jazzy.

Final status:

```text

                 ZED 2       D435i

                 -----       -----

Hardware          PASS        PASS

USB               PASS        PASS

ROS 2             PASS        PASS

RGB               PASS        PASS

Depth             PASS        PASS

PointCloud        PASS        PASS

IMU               PASS        PASS

Calibration/TF    PASS        PASS

```

The project therefore has two functioning RGB-D perception platforms.

**---**

**# 42. Phase 01 Completed**

```text

PHASE 01 – CAMERA & ROS 2

STATUS: COMPLETED

```

Validated cameras:

```text

Stereolabs ZED 2          COMPLETE

Intel RealSense D435i     COMPLETE

```

No additional camera-driver installation is currently required.

**---**



**---**

**# 42A. Fresh-System Reproduction Checklist**

To reproduce Phase 01 on another Ubuntu 24.04 + ROS 2 Jazzy machine:

```text
1. Install ROS 2 Jazzy.
2. Install NVIDIA driver/CUDA required by the selected ZED SDK.
3. Install the ZED SDK.
4. Clone this project with --recurse-submodules.
5. Run rosdep for the ZED workspace.
6. Build only from ros2_ws/src; build/install/log remain local.
7. Test the ZED 2 with ZED_Diagnostic and ZED_Depth_Viewer.
8. Launch the ZED ROS 2 wrapper and validate RGB/Depth/PointCloud/IMU.
9. Install librealsense and the ROS 2 Jazzy RealSense packages.
10. Test the D435i with realsense-viewer and rs-enumerate-devices.
11. Launch realsense2_camera and validate RGB/Depth/Aligned Depth/PointCloud/Gyro/Accel.
12. Use the troubleshooting commands in this README if USB or HID instability appears.
```


**# 43. Next Phase**

Next:

```text

Phase 02 – 2D Perception

```

Primary camera:

```text

ZED 2

```

Initial architecture:

```text

ZED 2

  │

  ▼

ZED ROS 2 Wrapper

  │

  ▼

ROS 2 RGB Image Topic

  │

  ▼

Python ROS 2 Node

  │

  ▼

cv_bridge

  │

  ▼

OpenCV

  │

  ▼

2D Image Processing

  │

  ▼

2D Perception

```

Phase 02 will move from camera-driver validation to our own perception code.

The purpose is to understand the complete path:

```text

Camera

→ ROS 2 Image

→ Python

→ OpenCV

→ Image Processing

→ Perception Result

→ ROS 2 Output

```

This becomes the foundation for the later AI perception, segmentation, 3D perception, manipulation and imitation-learning phases.
