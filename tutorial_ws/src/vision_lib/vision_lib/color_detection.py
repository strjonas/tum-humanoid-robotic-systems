"""Image-processing functions independent of ROS."""

import cv2
import numpy as np


def comp_mask(img, h_low, h_high, s_low, s_high, v_low, v_high):
    if h_low > h_high:
        lower_bound_1 = np.array([0, s_low, v_low])
        upper_bound_1 = np.array([h_high, s_high, v_high])
        lower_bound_2 = np.array([h_low, s_low, v_low])
        upper_bound_2 = np.array([179, s_high, v_high])

        mask1 = cv2.inRange(img, lower_bound_1, upper_bound_1)
        mask2 = cv2.inRange(img, lower_bound_2, upper_bound_2)
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        lower_bound = np.array([h_low, s_low, v_low])
        upper_bound = np.array([h_high, s_high, v_high])
        mask = cv2.inRange(img, lower_bound, upper_bound)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)


def get_circle(mask, min_dist, param1, param2, min_radius, max_radius):
    blurred = cv2.GaussianBlur(mask, (9, 9), 2)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1,
        minDist=min_dist, param1=param1, param2=param2,
        minRadius=min_radius, maxRadius=max_radius)
    if circles is None:
        return []
    return [((int(round(x)), int(round(y))), int(round(r)))
            for x, y, r in circles[0]]


def get_largest_contour(mask, min_area):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rel_contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= min_area]
    return max(rel_contours, key=cv2.contourArea, default=None)


def get_centroid(contour):
    moments = cv2.moments(contour)
    if moments['m00'] == 0:
        return None
    cx = int(moments['m10'] / moments['m00'])
    cy = int(moments['m01'] / moments['m00'])
    return (cx, cy)
