import cv2
import numpy as np

import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import Image


class ObjectTo3D(Node):

    def __init__(self):
        super().__init__('object_to_3d')

        self.bridge = CvBridge()

        qos = QoSProfile(depth=10)
        qos.reliability = QoSReliabilityPolicy.RELIABLE

        self.rgb_image = None
        self.depth_image = None

        self.rgb_subscription = self.create_subscription(
            Image,
            '/zed/zed_node/rgb/color/rect/image',
            self.rgb_callback,
            qos,
        )

        self.depth_subscription = self.create_subscription(
            Image,
            '/zed/zed_node/depth/depth_registered',
            self.depth_callback,
            qos,
        )

        self.get_logger().info(
            'Listening to RGB and registered depth images'
        )

    def rgb_callback(self, msg):
        self.rgb_image = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8',
        )

        self.process()

    def depth_callback(self, msg):
        self.depth_image = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='32FC1',
        )

    def process(self):
        if self.rgb_image is None or self.depth_image is None:
            return

        image = self.rgb_image.copy()

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Red object: two HSV ranges are needed because red wraps around.
        lower_red_1 = np.array([0, 100, 80])
        upper_red_1 = np.array([10, 255, 255])

        lower_red_2 = np.array([170, 100, 80])
        upper_red_2 = np.array([179, 255, 255])

        mask_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
        mask_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

        mask = cv2.bitwise_or(mask_1, mask_2)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        valid_contours = [
            contour
            for contour in contours
            if cv2.contourArea(contour) > 500
        ]

        if valid_contours:
            contour = max(valid_contours, key=cv2.contourArea)

            x, y, w, h = cv2.boundingRect(contour)

            u = x + w // 2
            v = y + h // 2

            if (
                0 <= v < self.depth_image.shape[0]
                and 0 <= u < self.depth_image.shape[1]
            ):
                z = float(self.depth_image[v, u])

                if np.isfinite(z) and z > 0.0:
                    # Approximate ZED 2 intrinsics for this learning step.
                    # Exact calibration values will be read from CameraInfo later.
                    fx = 700.0
                    fy = 700.0

                    cx = self.depth_image.shape[1] / 2.0
                    cy = self.depth_image.shape[0] / 2.0

                    X = (u - cx) * z / fx
                    Y = (v - cy) * z / fy
                    Z = z

                    cv2.rectangle(
                        image,
                        (x, y),
                        (x + w, y + h),
                        (0, 255, 0),
                        2,
                    )

                    cv2.drawMarker(
                        image,
                        (u, v),
                        (0, 255, 255),
                        cv2.MARKER_CROSS,
                        25,
                        2,
                    )

                    text = (
                        f'X={X:.3f} m  '
                        f'Y={Y:.3f} m  '
                        f'Z={Z:.3f} m'
                    )

                    cv2.putText(
                        image,
                        text,
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2,
                    )

                    self.get_logger().info(
                        f'Object center ({u}, {v}) -> '
                        f'X={X:.3f} m, '
                        f'Y={Y:.3f} m, '
                        f'Z={Z:.3f} m'
                    )
                else:
                    cv2.putText(
                        image,
                        'Object detected - invalid depth',
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2,
                    )

        cv2.imshow('ZED 2 - Object Localization', image)
        cv2.imshow('ZED 2 - Object Mask', mask)

        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)

    node = ObjectTo3D()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()

        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
