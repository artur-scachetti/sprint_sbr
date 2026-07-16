#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data
from sprint_sbr.msg import Object, ObjectArray
import math

class PerceptionNode(Node):
    def __init__(self):

        super().__init__('perception_node')

        self.declare_parameter('boat_name', 'alfa')
        self.declare_parameter('max_range', 100.0)
        self.declare_parameter('cluster_threshold', 2.0)

        self.boat_name = self.get_parameter('boat_name').get_parameter_value().string_value
        self.max_range = self.get_parameter('max_range').get_parameter_value().double_value
        self.cluster_threshold = self.get_parameter('cluster_threshold').get_parameter_value().double_value

        lidar_topic = f'/{self.boat_name}/lidar'
        self.subscription = self.create_subscription(
            LaserScan,
            lidar_topic,
            self.lidar_callback,
            qos_profile_sensor_data
        )

        perception_topic = f'/{self.boat_name}/perception/objects'
        self.publisher = self.create_publisher(ObjectArray, perception_topic, 10)

        self.get_logger().info(f"monitorando lidar do barco {self.boat_name} com range {self.max_range}")

    def lidar_callback(self, msg):

        self.get_logger().info("debug de callback do lidar")

        objects = self.extract_objects(msg)

        msg_out = ObjectArray()

        for obj in objects:

            obj_msg = Object()
            obj_msg.distance = float(obj['min_dist'])
            obj_msg.angle = float(obj['angle'])

            msg_out.objects.append(obj_msg)
        
        self.publisher.publish(msg_out)
    

    def extract_objects(self, msg):

        clusters = []
        current_cluster = []
        angle = msg.angle_min

        for r in msg.ranges:

            if not math.isinf(r) and not math.isnan(r) and r <= self.max_range:

                point_data = {'dist': r, 'angle': angle}

                if not current_cluster:
                    current_cluster.append(point_data)

                else:
                    last_point = current_cluster[-1]
                    dist_diff = abs(r - last_point['dist'])

                    if dist_diff <= self.cluster_threshold:
                        current_cluster.append(point_data)
                    
                    else:
                        clusters.append(current_cluster)
                        current_cluster = [point_data]
                
            angle += msg.angle_increment

        if current_cluster:
            clusters.append(current_cluster)

        processed_objects = []

        for cluster in clusters:
            closest_point = min(cluster, key=lambda x: x['dist'])
            processed_objects.append({
                'min_dist' : closest_point['dist'],
                'angle' : closest_point['angle']
            })

        return processed_objects
    
def main(args=None):

    rclpy.init(args=args)
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()




