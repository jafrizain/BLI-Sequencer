import cv2
import numpy as np
from mask import mask

intensities = mask('Processing/wellplate2_undistorted_grey_edgedetected.jpg', 'Processing/wellplate2_undistorted.jpg')

print(intensities)
