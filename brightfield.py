import time
import sys
import os
import RPi.GPIO as GPIO
from picamera import PiCamera

# Setup GPIO
LED_PIN = 17
LED_PIN2 = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(LED_PIN2, GPIO.OUT)

# Check if an argument was provided
if len(sys.argv) < 2:
    print("Usage: python3 brightfield.py <exposure_time> <filename>")
    sys.exit(1)

# Get command-line arguments
exposure_time = float(sys.argv[1])  # Time for each exposure
file_name = str(sys.argv[2])        # Root file name

# Turn LED on
GPIO.output(LED_PIN, GPIO.HIGH)
GPIO.output(LED_PIN2, GPIO.HIGH)

camera = PiCamera(resolution=(1280, 720))
camera.shutter_speed = int(exposure_time*1000000)
camera.iso = 800
time.sleep(10)
camera.exposure_mode = 'off'
camera.capture(file_name)

# Turn LED off
GPIO.output(LED_PIN, GPIO.LOW)
GPIO.output(LED_PIN2, GPIO.LOW)

print("Image capture process complete.")

# Cleanup GPIO
GPIO.cleanup()
