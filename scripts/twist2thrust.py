#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

class Twist2Thrust(Node):
    def __init__(self):
        
        super().__init__('twist2thrust')

        # pega o nome do barco como parametro para subscriber e publisher (caso default -> alfa)
        self.declare_parameter('boat_name', 'alfa')
        boat_name = self.get_parameter('boat_name').get_parameter_value().string_value

        self.subcription = self.create_subscription(
            Twist,
            f'/{boat_name}/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.left_pub = self.create_publisher(Float64, f'{boat_name}/thrusters/left/thrust', 10)
        self.right_pub = self.create_publisher(Float64, f'{boat_name}/thrusters/right/thrust', 10)
        self.get_logger().info(f't2t iniciado -> controlando barco: {boat_name}')

        self.declare_parameter('linear_gain', 5000.0)
        self.declare_parameter('angular_gain', 5000.0)

    def cmd_vel_callback(self, msg):

        linear_gain = self.get_parameter('linear_gain').value
        angular_gain = self.get_parameter('angular_gain').value

        v = msg.linear.x * linear_gain
        w = msg.angular.z * angular_gain

        left_cmd = v - w
        right_cmd = v + w

        max_thrust = 5000.0
        left_cmd = max(-max_thrust, min(max_thrust, left_cmd))
        right_cmd = max(-max_thrust, min(max_thrust, right_cmd))
        
        msg_left = Float64()
        msg_left.data = float(left_cmd)

        msg_right = Float64()
        msg_right.data = float(right_cmd)

        self.get_logger().info(f"v: {v:.2f}, w: {w:.2f} -> L_thrust: {left_cmd:.2f}, R_thrust: {right_cmd:.2f}")

        self.left_pub.publish(msg_left)
        self.right_pub.publish(msg_right)

def main(args=None):
    rclpy.init(args=args)
    node = Twist2Thrust()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()