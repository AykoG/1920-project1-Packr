import RPi.GPIO as GPIO
import time

servoPIN = 20
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50)
p.start(2.5)
try:
  while True:
    p.ChangeDutyCycle(2.5)
    time.sleep(2)
    p.ChangeDutyCycle(7.5)
    time.sleep(2)
except KeyboardInterrupt:
  p.stop()
  GPIO.cleanup()