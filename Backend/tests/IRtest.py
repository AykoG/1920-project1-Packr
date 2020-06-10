import time
from RPi import GPIO

SENSORPIN = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSORPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#sensorState = 0
#lastState = 0

def IR_callback(channel):
    print("callback")

GPIO.add_event_detect(SENSORPIN, GPIO.FALLING, callback=IR_callback, bouncetime=100)

while True:
  #sensorState = GPIO.input(SENSORPIN)
  #if (sensorState and not lastState):
  #  print("Unbroken")
  #if (not sensorState and lastState):
  #  print("Broken")
  #lastState = sensorState
  time.sleep(0.01)