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
