import rclpy

from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from rclpy.time import Time
from tf2_geometry_msgs import do_transform_point
from tf2_ros import Buffer, TransformException, TransformListener
from zed_msgs.msg import ObjectsStamped


class ObjectToRobotFrame(Node):

    def __init__(self):
        super().__init__('object_to_robot_frame')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer,
            self,
        )

        self.subscription = self.create_subscription(
            ObjectsStamped,
            '/zed/zed_node/obj_det/objects',
            self.objects_callback,
            10,
        )

        self.get_logger().info(
            'Object localization: zed_left_camera_frame -> robot_base'
        )

    def objects_callback(self, msg):

        for obj in msg.objects:

            if len(obj.position) < 3:
                continue

            camera_point = PointStamped()

            camera_point.header.frame_id = msg.header.frame_id
            camera_point.header.stamp = msg.header.stamp

            camera_point.point.x = float(obj.position[0])
            camera_point.point.y = float(obj.position[1])
            camera_point.point.z = float(obj.position[2])

            try:
                transform = self.tf_buffer.lookup_transform(
                    'robot_base',
                    camera_point.header.frame_id,
                    Time(),
                )

                robot_point = do_transform_point(
                    camera_point,
                    transform,
                )

            except TransformException as exc:
                self.get_logger().warning(
                    f'Transform unavailable: {exc}'
                )
                return

            label = obj.sublabel if obj.sublabel else obj.label

            self.get_logger().info(
                f'{label} | '
                f'camera=({camera_point.point.x:.3f}, '
                f'{camera_point.point.y:.3f}, '
                f'{camera_point.point.z:.3f}) m | '
                f'robot_base=({robot_point.point.x:.3f}, '
                f'{robot_point.point.y:.3f}, '
                f'{robot_point.point.z:.3f}) m'
            )


def main(args=None):
    rclpy.init(args=args)

    node = ObjectToRobotFrame()

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
