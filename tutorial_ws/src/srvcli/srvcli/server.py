
import rclpy
from rclpy.node import Node
from tutorial_interfaces.srv import StringProcess


class StringServer(Node):

    def __init__(self):
        super().__init__('string_server')
        self.srv = self.create_service(
            StringProcess, 'process_string', self.process_string_callback)

    def process_string_callback(self, request, response):
        """Return the reversed text and an exact palindrome comparison."""
        response.reversed_text = request.text[::-1]
        response.is_palindrome = request.text == response.reversed_text
        return response


def main(args=None):
    rclpy.init(args=args)
    node = StringServer()
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
