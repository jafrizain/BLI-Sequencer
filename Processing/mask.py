import cv2
import numpy as np

def mask(brightfield_im, darkfield_im):

    bright = cv2.imread(brightfield_im)
    dark = cv2.imread(darkfield_im)

    gray_bright = cv2.cvtColor(bright, cv2.COLOR_BGR2GRAY) 
    gray_dark = cv2.cvtColor(dark, cv2.COLOR_BGR2GRAY) #Replace with RAW to processed function. Should result in 16bit greyscale
    gray = cv2.equalizeHist(gray_bright)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.00009,
        minDist=50,        # Minimum distance between centers
        param1=269,         # Upper threshold for Canny edge detector
        param2=22,         # Threshold for center detection
        minRadius=20,       # Adjust depending on well size
        maxRadius=28
    )

    intensities = []

    mask_save = np.zeros_like(gray, dtype=np.uint8)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in range (len(circles[0])):
            mask = np.zeros_like(gray, dtype=np.uint8)
            c = circles[0][i]
            print(c)
            print(i)
            cv2.circle(mask, (c[0], c[1]), 27, 255, thickness=-1)  # filled white circles
            mask_save = mask_save + mask
            intensity = np.sum(mask*gray_dark)
            intensities.append(intensity)

    cv2.imwrite(brightfield_im[:-4] + "_mask.jpg", mask_save)
    return(intensities)
