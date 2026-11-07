from my_other_python_libs.other_python_lib_1 import say_it_again
from my_other_python_libs.other_python_lib_2 import libpy3
from my_python_libs.python_lib_1 import say_it_works
from my_python_libs.python_lib_2 import libpy2
import rclpy
from rclpy.node import Node


class TestImport2(Node):
    def __init__(self):
        super().__init__('test_import_2')

        self.lib2 = libpy2()
        self.lib3 = libpy3()

    def main(self):
        say_it_works()
        say_it_again()
        self.lib2.say_it_too(self)
        self.lib2.calculate(self)
        self.lib3.say_it_too(self)
        self.lib3.calculate(self)


def main():
    rclpy.init()
    node = TestImport2()
    node.main()
    node.destroy_node()
    rclpy.shutdown()
