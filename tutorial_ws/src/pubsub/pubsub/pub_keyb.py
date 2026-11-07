import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class PubKeyb(Node):

    def __init__(self):
        super().__init__('keyboard_publisher')
        self.publisher_ = self.create_publisher(String, 'keys', 10)

    def on_key(self, key):
        msg = String()
        msg.data = str(key)
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    keyboard_publisher = PubKeyb()
    try:
        while rclpy.ok():
            key = input('Enter text and press Enter: ')
            keyboard_publisher.on_key(key)
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        keyboard_publisher.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
