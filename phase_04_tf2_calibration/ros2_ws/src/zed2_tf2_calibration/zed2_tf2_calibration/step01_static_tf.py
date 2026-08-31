import rclpy

from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster


class StaticCameraTransform(Node):

    def __init__(self):
        super().__init__('static_camera_transform')

        self.broadcaster = StaticTransformBroadcaster(self)

        transform = TransformStamped()

        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = 'robot_base'
        transform.child_frame_id = 'zed_left_camera_frame'

        # Example translation:
        # Camera is 0.50 m in front of the robot base
        # and 0.80 m above it.
        transform.transform.translation.x = 0.50
        transform.transform.translation.y = 0.00
        transform.transform.translation.z = 0.80

        # No rotation for the first TF2 exercise.
        transform.transform.rotation.x = 0.0
        transform.transform.rotation.y = 0.0
        transform.transform.rotation.z = 0.0
        transform.transform.rotation.w = 1.0

        self.broadcaster.sendTransform(transform)

        self.get_logger().info(
            'Published static transform: robot_base -> zed_left_camera_frame'
        )


def main(args=None):
    rclpy.init(args=args)

    node = StaticCameraTransform()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
