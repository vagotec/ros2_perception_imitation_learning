import rclpy

from geometry_msgs.msg import PointStamped
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from tf2_geometry_msgs import do_transform_point
from tf2_ros import Buffer, TransformException, TransformListener


class TransformPointNode(Node):

    def __init__(self):
        super().__init__('transform_point')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer,
            self,
        )

        self.timer = self.create_timer(
            1.0,
            self.transform_point,
        )

        self.done = False

    def transform_point(self):
        if self.done:
            return

        point_camera = PointStamped()

        point_camera.header.frame_id = 'zed_left_camera_frame'
        point_camera.header.stamp = self.get_clock().now().to_msg()

        # Example point measured in the camera frame.
        point_camera.point.x = 1.00
        point_camera.point.y = 0.10
        point_camera.point.z = -0.05

        try:
            transform = self.tf_buffer.lookup_transform(
                'robot_base',
                'zed_left_camera_frame',
                Time(),
                timeout=Duration(seconds=1.0),
            )

            point_robot = do_transform_point(
                point_camera,
                transform,
            )

            self.get_logger().info(
                'Camera frame: '
                f'x={point_camera.point.x:.3f}, '
                f'y={point_camera.point.y:.3f}, '
                f'z={point_camera.point.z:.3f}'
            )

            self.get_logger().info(
                'Robot base frame: '
                f'x={point_robot.point.x:.3f}, '
                f'y={point_robot.point.y:.3f}, '
                f'z={point_robot.point.z:.3f}'
            )

            self.done = True

        except TransformException as exc:
            self.get_logger().warning(
                f'Transform not available yet: {exc}'
            )


def main(args=None):
    rclpy.init(args=args)

    node = TransformPointNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
