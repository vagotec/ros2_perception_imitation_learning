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

            # 1. Grayscale
            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY,
            )

            # 2. Noise reduction
            blurred = cv2.GaussianBlur(
                gray,
                (5, 5),
                0,
            )

            # 3. Edge detection
            edges = cv2.Canny(
                blurred,
                50,
                150,
            )

            # 4. Find contours
            contours, _ = cv2.findContours(
                edges,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE,
            )

            result = frame.copy()

            # 5. Bounding boxes
            for contour in contours:

                area = cv2.contourArea(contour)

                # Ignore very small regions/noise
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

            # Show classical perception stages
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

            # 6. Publish processed image back to ROS 2
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
