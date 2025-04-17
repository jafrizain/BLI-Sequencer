import time
import sys
import os
import subprocess
from picamera import PiCamera
from fractions import Fraction


# Check if enough arguments were provided
if len(sys.argv) < 2:
    print("Usage: python3 darkfield.py <exposure_time> <file_name>")
    sys.exit(1)

# Get command-line arguments
exposure_time = float(sys.argv[1])  # Time for each exposure
file_name = str(sys.argv[2])        # Root file name

camera = PiCamera(
    resolution=(1280, 720),
    framerate=Fraction(1, 6),
    sensor_mode=3)
camera.shutter_speed = int(exposure_time*1000000)
camera.iso = 800
time.sleep(2)
camera.exposure_mode = 'off'
camera.capture(file_name)

print("Image capture process complete.")


