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
from sensor_msgs.msg import CameraInfo, Image


class PixelTo3DNode(Node):

    def __init__(self):
        super().__init__('pixel_to_3d')

        self.bridge = CvBridge()

        self.depth_image = None
        self.camera_info = None

        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.rgb_sub = self.create_subscription(
            Image,
            '/zed/zed_node/rgb/color/rect/image',
            self.rgb_callback,
            qos,
        )

        self.depth_sub = self.create_subscription(
            Image,
            '/zed/zed_node/depth/depth_registered',
            self.depth_callback,
            qos,
        )

        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            '/zed/zed_node/rgb/color/rect/camera_info',
            self.camera_info_callback,
            qos,
        )

        self.get_logger().info('Pixel-to-3D node started')

    def depth_callback(self, msg):
        self.depth_image = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='32FC1',
        )

    def camera_info_callback(self, msg):
        self.camera_info = msg

    def rgb_callback(self, msg):
        if self.depth_image is None or self.camera_info is None:
            return

        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8',
        )

        height, width = frame.shape[:2]

        u = width // 2
        v = height // 2

        depth = float(self.depth_image[v, u])

        if not math.isfinite(depth) or depth <= 0.0:
            text = '3D point: invalid depth'
        else:
            fx = self.camera_info.k[0]
            fy = self.camera_info.k[4]
            cx = self.camera_info.k[2]
            cy = self.camera_info.k[5]

            x = (u - cx) * depth / fx
            y = (v - cy) * depth / fy
            z = depth

            text = (
                f'X={x:.3f} m  '
                f'Y={y:.3f} m  '
                f'Z={z:.3f} m'
            )

            self.get_logger().info(
                f'Pixel ({u}, {v}) -> '
                f'X={x:.3f} m, '
                f'Y={y:.3f} m, '
                f'Z={z:.3f} m'
            )

        cv2.drawMarker(
            frame,
            (u, v),
            (0, 255, 255),
            cv2.MARKER_CROSS,
            25,
            2,
        )

        cv2.putText(
            frame,
            text,
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

        cv2.imshow(
            'ZED 2 - Pixel to 3D',
            frame,
        )

        cv2.waitKey(1)

    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = PixelTo3DNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
