#!/usr/bin/python

import RPi.GPIO as GPIO
from DHT11_class import DHT11_class
import time
import datetime

dht11_pin = 16
limit_sec = 300

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

sleep_time = 1
instance = DHT11_class(pin=dht11_pin)
previous_temperature = 0
previous_humidity = 0

try:
    print("DHT11 Module Test (CTRL+C to exit)")
    print("please wait...")
    time.sleep(2)
    now = datetime.datetime.now()
    print("Ready! "+ now.strftime("%d.%m.%Y") + " / " + now.strftime("%H:%M:%S"))
    result = instance.read()
    if result.is_valid():
        now = datetime.datetime.now()
        print("Initial valid input: " + now.strftime("%d.%m.%Y") + " / " + now.strftime("%H:%M:%S"))
        print("Temperature: %d C" % result.temperature)
        print("Humidity: %d %%" % result.humidity)
        print("*******************************************")

        previous_temperature = result.temperature
        previous_humidity = result.humidity
    else:
        pass

    counter = 0
    cnt = 0
    
    while True:

        cnt += 1
        if cnt%limit_sec == 0 or cnt == 1:

            result = instance.read()
            if result.is_valid():
                
                if previous_temperature != result.temperature or previous_humidity != result.humidity:

                    previous_temperature = result.temperature
                    previous_humidity = result.humidity
                
                    counter += 1
                    rightnow = datetime.datetime.now()
                    print(str(counter)+". Last valid input: " + rightnow.strftime("%d.%m.%Y") + " / " + rightnow.strftime("%H:%M:%S"))
                    print("Temperature: %d C" % result.temperature)
                    print("Humidity: %d %%" % result.humidity)
                    print("*******************************************")
            else:
                pass

        time.sleep(sleep_time)
        
except KeyboardInterrupt:
        print(" Quit")
        GPIO.cleanup()