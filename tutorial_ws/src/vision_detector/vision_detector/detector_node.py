import cv2
import numpy as np
from rcl_interfaces.msg import IntegerRange, ParameterDescriptor
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from tutorial_interfaces.msg import Detection
from tutorial_interfaces.srv import SetTarget
from vision_lib import color_detection


class ColorDetector(Node):
    def __init__(self):
        super().__init__('color_detector')

        self.subscription = self.create_subscription(
            CompressedImage,
            'camera_image/compressed',
            self.frame_callback,
            10
        )

        self.publisher = self.create_publisher(Detection, '/detection', 10)

        self.change_target_service = self.create_service(
            SetTarget,
            '/set_target',
            self.set_target_callback
        )

        # Cache the frame so parameters can be tuned while playback is paused.
        self.current_img = None

        cv2.namedWindow('Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Detection', 640, 480)

        # Refresh paused frames so parameter changes remain visible.
        self.timer = self.create_timer(1.0, self.render_callback)

        def descriptor(from_val: int, to_val: int) -> ParameterDescriptor:
            return ParameterDescriptor(
                integer_range=[
                    IntegerRange(from_value=from_val, to_value=to_val, step=1)
                ]
            )

        default_params = {
            'red_cube': {
                'h_low': 170, 'h_high': 2,
                's_low': 80,  's_high': 212,
                'v_low': 210, 'v_high': 255,
            },
            'green_cube': {
                'h_low': 26,  'h_high': 91,
                's_low': 57,  's_high': 178,
                'v_low': 120, 'v_high': 233,
            },
            'purple_ball': {
                'h_low': 137, 'h_high': 175,
                's_low': 43,  's_high': 255,
                'v_low': 30,  'v_high': 255,
            },
        }

        self.objects = list(default_params.keys())

        target_object_descriptor = ParameterDescriptor(
            description='Target object to detect',
            type=rclpy.Parameter.Type.STRING,
            additional_constraints=', '.join(self.objects)
        )
        self.declare_parameter('target_object', 'red_cube', target_object_descriptor)

        for obj, vals in default_params.items():
            self.declare_parameter(f'{obj}.h_low', vals['h_low'], descriptor(0, 179))
            self.declare_parameter(f'{obj}.h_high', vals['h_high'], descriptor(0, 179))
            self.declare_parameter(f'{obj}.s_low', vals['s_low'], descriptor(0, 255))
            self.declare_parameter(f'{obj}.s_high', vals['s_high'], descriptor(0, 255))
            self.declare_parameter(f'{obj}.v_low', vals['v_low'], descriptor(0, 255))
            self.declare_parameter(f'{obj}.v_high', vals['v_high'], descriptor(0, 255))

        self.declare_parameter('min_area', 150)
        self.declare_parameter('circle.min_dist', 50, descriptor(1, 640))
        self.declare_parameter('circle.param1', 50, descriptor(1, 255))
        self.declare_parameter('circle.param2', 18, descriptor(1, 100))
        self.declare_parameter('circle.min_radius', 20, descriptor(0, 240))
        self.declare_parameter('circle.max_radius', 85, descriptor(1, 240))

    def set_target_callback(self, request, response):
        response.success = request.target in self.objects
        if response.success:
            self.set_parameters([rclpy.Parameter(
                'target_object', rclpy.Parameter.Type.STRING, request.target)])
        return response

    def render_callback(self):
        self.update()

    def update(self, publish=False):
        frame = self.current_img
        target_object = self.get_parameter('target_object').value
        if frame is None:
            return

        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        thresholds = {
            name: self.get_parameter(f'{target_object}.{name}').value
            for name in ['h_low', 'h_high', 's_low', 's_high', 'v_low', 'v_high']
        }
        mask = color_detection.comp_mask(hsv_image, **thresholds)

        det_window = frame.copy()
        contour = color_detection.get_largest_contour(
            mask, self.get_parameter('min_area').value)

        centroid = None
        if contour is not None:
            centroid = color_detection.get_centroid(contour)
            if centroid is not None:
                cv2.drawMarker(
                    det_window, centroid, (0, 255, 0),
                    markerType=cv2.MARKER_CROSS, markerSize=10, thickness=2)

        radius = -1
        if target_object == 'purple_ball':
            circle_params = {
                name: self.get_parameter(f'circle.{name}').value
                for name in ['min_dist', 'param1', 'param2', 'min_radius', 'max_radius']
            }
            circles = color_detection.get_circle(mask, **circle_params)
            for circle in circles:
                cv2.circle(det_window, circle[0], circle[1], (0, 255, 0), 2)
            cv2.putText(det_window, f'Circles: {len(circles)}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            if circles:
                largest_circle = max(circles, key=lambda c: c[1])
                radius = largest_circle[1]

        if publish:
            self.publish_detection(contour, centroid, target_object, radius)

        cv2.imshow('Detection', det_window)
        cv2.imshow('Camera', frame)
        cv2.imshow('Mask', mask)
        cv2.waitKey(1)

    def publish_detection(self, contour, centroid, target_object, radius):

        detection_msg = Detection()
        detection_msg.target = target_object
        detection_msg.radius = -1.0
        detection_msg.found = (
            contour is not None and centroid is not None and
            (target_object != 'purple_ball' or radius >= 0))
        if detection_msg.found:
            detection_msg.x = float(centroid[0])
            detection_msg.y = float(centroid[1])
            detection_msg.area = cv2.contourArea(contour)
            if target_object == 'purple_ball':
                detection_msg.radius = float(radius)
        else:
            detection_msg.x = -1.0
            detection_msg.y = -1.0
            detection_msg.area = -1.0

        self.publisher.publish(detection_msg)

    def frame_callback(self, msg):

        self.current_img = cv2.imdecode(np.frombuffer(msg.data, np.uint8), cv2.IMREAD_COLOR)

        self.update(publish=True)


def main():
    rclpy.init()
    node = ColorDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
