import math

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    QoSReliabilityPolicy,
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
)
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2


class ZedPointCloudXYZ(Node):

    def __init__(self):
        super().__init__('zed_pointcloud_xyz')

        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.subscription = self.create_subscription(
            PointCloud2,
            '/zed/zed_node/point_cloud/cloud_registered',
            self.pointcloud_callback,
            qos,
        )

        self.get_logger().info(
            'Listening to /zed/zed_node/point_cloud/cloud_registered'
        )

    def pointcloud_callback(self, msg):
        center_u = msg.width // 2
        center_v = msg.height // 2

        center_index = center_v * msg.width + center_u

        points = point_cloud2.read_points(
            msg,
            field_names=('x', 'y', 'z'),
            skip_nans=False,
            uvs=[center_index],
        )

        if len(points) == 0:
            self.get_logger().info('Center point: unavailable')
            return

        point = points[0]

        x = float(point['x'])
        y = float(point['y'])
        z = float(point['z'])

        if all(math.isfinite(value) for value in (x, y, z)):
            self.get_logger().info(
                f'Center pixel ({center_u}, {center_v}) -> '
                f'x={x:.3f} m, '
                f'y={y:.3f} m, '
                f'z={z:.3f} m'
            )
        else:
            self.get_logger().info(
                f'Center pixel ({center_u}, {center_v}) -> invalid 3D point'
            )


def main(args=None):
    rclpy.init(args=args)

    node = ZedPointCloudXYZ()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
