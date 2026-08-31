import math

import cv2
import rclpy

from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import Image
from zed_msgs.msg import ObjectsStamped


class ZedObjectDetection(Node):

    def __init__(self):
        super().__init__('zed_object_detection')

        self.bridge = CvBridge()
        self.objects = []

        qos = QoSProfile(depth=10)
        qos.reliability = QoSReliabilityPolicy.RELIABLE

        self.image_sub = self.create_subscription(
            Image,
            '/zed/zed_node/rgb/color/rect/image',
            self.image_callback,
            qos,
        )

        self.objects_sub = self.create_subscription(
            ObjectsStamped,
            '/zed/zed_node/obj_det/objects',
            self.objects_callback,
            qos,
        )

        self.get_logger().info(
            'Listening to ZED RGB and native Object Detection'
        )

    def objects_callback(self, msg):
        self.objects = msg.objects

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8',
        )

        for obj in self.objects:
            corners = obj.bounding_box_2d.corners

            if len(corners) < 4:
                continue

            x1 = int(corners[0].kp[0])
            y1 = int(corners[0].kp[1])
            x2 = int(corners[2].kp[0])
            y2 = int(corners[2].kp[1])

            x1 = max(0, min(x1, frame.shape[1] - 1))
            x2 = max(0, min(x2, frame.shape[1] - 1))
            y1 = max(0, min(y1, frame.shape[0] - 1))
            y2 = max(0, min(y2, frame.shape[0] - 1))

            position = obj.position

            if len(position) >= 3:
                x = float(position[0])
                y = float(position[1])
                z = float(position[2])
            else:
                x = y = z = float('nan')

            label = obj.sublabel if obj.sublabel else obj.label

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            center_u = (x1 + x2) // 2
            center_v = (y1 + y2) // 2

            cv2.drawMarker(
                frame,
                (center_u, center_v),
                (0, 255, 255),
                cv2.MARKER_CROSS,
                20,
                2,
            )

            if all(math.isfinite(value) for value in (x, y, z)):
                text = (
                    f'{label} {obj.confidence:.1f}% '
                    f'X={x:.3f} Y={y:.3f} Z={z:.3f} m'
                )

                self.get_logger().info(
                    f'{label}: '
                    f'confidence={obj.confidence:.1f}% '
                    f'position=({x:.3f}, {y:.3f}, {z:.3f}) m'
                )
            else:
                text = (
                    f'{label} {obj.confidence:.1f}% '
                    f'3D position invalid'
                )

            cv2.putText(
                frame,
                text,
                (x1, max(30, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

        cv2.imshow(
            'ZED 2 - Native Object Detection + 3D',
            frame,
        )

        cv2.waitKey(1)

    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = ZedObjectDetection()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
