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

            cv2.imshow('ZED 2 - ROS 2 RGB', image)
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
