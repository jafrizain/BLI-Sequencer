import cv2
import numpy as np


# Load the image
img = cv2.imread('Processing/wellplate2.jpg')
h, w = img.shape[:2]

# Estimate camera matrix for fisheye lens
fov_deg = 60
fov_rad = np.deg2rad(fov_deg)
f = 0.5 * w / np.tan(0.5 * fov_rad)  # approximate focal length

K = np.array([[f, 0, w / 2],
              [0, f, h / 2],
              [0, 0, 1]])

# Assume some fisheye distortion coefficients (typical values)
D = np.array([-0.3, 0.1, 0, 0])  # You can tweak these for better results

# Undistort
map1, map2 = cv2.fisheye.initUndistortRectifyMap(
    K, D, np.eye(3), K, (w, h), cv2.CV_16SC2)
undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR)

# Save result
cv2.imwrite('Processing/wellplate2_undistorted.jpg', undistorted_img)
