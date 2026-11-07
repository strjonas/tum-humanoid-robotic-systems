"""Send keyboard input to the string processing service."""

import rclpy
from rclpy.node import Node
from tutorial_interfaces.srv import StringProcess


class StringClient(Node):
    """Call the string processing service asynchronously."""

    def __init__(self):
        super().__init__('string_client')
        self.cli = self.create_client(StringProcess, 'process_string')

    def send_request(self, text):
        """Send one string and return a future for its response."""
        request = StringProcess.Request()
        request.text = text
        return self.cli.call_async(request)


def main(args=None):
    """Read and process lines until Ctrl+C or end of input."""
    rclpy.init(args=args)
    node = StringClient()
    try:
        while not node.cli.wait_for_service(timeout_sec=1.0):
            node.get_logger().info('service not available, waiting again...')
        while rclpy.ok():
            text = input('Enter text and press Enter: ')
            future = node.send_request(text)
            rclpy.spin_until_future_complete(node, future)
            response = future.result()
            node.get_logger().info(
                f'Reversed: {response.reversed_text}\n'
                f'Palindrome: {response.is_palindrome}')
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
