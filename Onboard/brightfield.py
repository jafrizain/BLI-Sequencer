import time
import sys
import os
import RPi.GPIO as GPIO
from picamera2 import Picamera2, Preview
from libcamera import controls

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

camera = Picamera2()
camera.start_preview(Preview.NULL)

# initalizing camera
preview_config = camera.create_preview_configuration()
capture_config = camera.create_still_configuration(raw={}, display=None)
camera.configure(preview_config)

camera.set_controls({

    "ExposureTime": int(exposure_time * (1 * 10^6)),
    "AeEnable": False,
    "AwbEnable": False,
    "AnalogueGain": 1,          # Analog gain
    "NoiseReductionMode": controls.draft.NoiseReductionModeEnum.Off  # Disable noise reduction

})

time.sleep(10)

camera.start()

r = camera.switch_mode_capture_request_and_stop(capture_config)
r.save("main", file_name + ".jpg")
r.save_dng(file_name + ".dng")

camera.stop()

# Turn LED off
GPIO.output(LED_PIN, GPIO.LOW)
GPIO.output(LED_PIN2, GPIO.LOW)

print("Image capture process complete.")

# Cleanup GPIO
GPIO.cleanup()