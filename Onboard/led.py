import RPi.GPIO as GPIO
import time
import sys

LED_PIN = 17
LED_PIN2 = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(LED_PIN2, GPIO.OUT)

GPIO.output(LED_PIN, GPIO.HIGH)
GPIO.output(LED_PIN2, GPIO.HIGH)
time.sleep(1.0)
GPIO.output(LED_PIN, GPIO.LOW)
GPIO.output(LED_PIN2, GPIO.LOW)
time.sleep(1.0)
GPIO.output(LED_PIN, GPIO.HIGH)
GPIO.output(LED_PIN2, GPIO.HIGH)
time.sleep(1.0)
GPIO.output(LED_PIN, GPIO.LOW)
GPIO.output(LED_PIN2, GPIO.LOW)

GPIO.cleanup()

	

