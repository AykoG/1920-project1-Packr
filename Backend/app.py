from repositories.DataRepository import DataRepository
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

import time
import threading
import subprocess

import os
import spidev
import datetime
import serial
from RPi import GPIO
from model.LCD_class import LCD_class
from subprocess import check_output
from model.SPI_class import SPI_class
from model.DHT11_class import DHT11_class

LCD_E = 24
LCD_RS = 25
LCD_pinnen = [17, 27, 22, 5, 6, 13, 19, 26]
SER_pinnen = [20, 21]
HUM_dht11 = 16
IR1_pin = 4
IR2_pin = 18

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8z#2HzSIuJdj&b'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

print("Code gestart")
mijn_lcd = LCD_class(LCD_E, LCD_RS, LCD_pinnen)
mijn_lcd.init_LCD()

tmp = SPI_class()

for pin in SER_pinnen:
    GPIO.setup(pin, GPIO.OUT)
motor1 = GPIO.PWM(SER_pinnen[0], 50)
motor2 = GPIO.PWM(SER_pinnen[1], 50)
motor1.start(2.5)
motor2.start(2.5)

instance = DHT11_class(pin=HUM_dht11)

GPIO.setup(IR1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(IR2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def clear_display():
    mijn_lcd.clear_display()
    mijn_lcd.write_message("Connecting...", "1")
    ips = str(check_output(['hostname', '--all-ip-addresses']))
    ips = ips.replace("b","").replace("'","")
    ips = ips.split(" ")
    while len(ips[1]) < 5:
        ips = str(check_output(['hostname', '--all-ip-addresses']))
        ips = ips.replace("b","").replace("'","")
        ips = ips.split(" ")
    mijn_lcd.write_message(ips[1], "1")

def IR_callback(channel):
    if channel == IR1_pin:
        execute_device({'apparaat_id': 'IR1', 'geforceerde_waarde': 0 })
    elif channel == IR2_pin:
        execute_device({'apparaat_id': 'IR2', 'geforceerde_waarde': 0 })

def motor_open():
    motor1.ChangeDutyCycle(2.5)
    motor2.ChangeDutyCycle(2.5)
    return 1

def motor_close():
    motor1.ChangeDutyCycle(7.5)
    motor2.ChangeDutyCycle(7.5)
    return 0


GPIO.add_event_detect(IR1_pin, GPIO.FALLING, callback=IR_callback, bouncetime=500)
GPIO.add_event_detect(IR2_pin, GPIO.FALLING, callback=IR_callback, bouncetime=500)

clear_display()

# API ENDPOINTS
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

@app.route('/api/v1/metingen', methods=['GET'])
def get_metingen():
    if request.method == 'GET':
        return jsonify(metingen=DataRepository.read_metingen()), 200

@app.route('/api/v1/metingen/<apparaatid>', methods=['GET'])
def get_metingen_per_id(apparaatid):
    if request.method == 'GET':
        return jsonify(metingen=DataRepository.read_metingen_per_id(apparaatid)), 200

@app.route('/api/v1/metingen/IR/<apparaatid>', methods=['GET'])
def get_metingen_per_id_IR(apparaatid):
    if request.method == 'GET':
        return jsonify(metingen=DataRepository.read_metingen_per_id_IR(apparaatid)), 200

# SOCKET IO
@socketio.on('connect')
def initial_connection():
    print('A new client connect')

@socketio.on('F2B_read_status')
def read_status():
    #read_metingen()
    apparaten = DataRepository.read_apparaten()
    for apparaat in apparaten:
        read_latest_meting_per_id(apparaat['apparaatid'])

@socketio.on('F2B_read_metingen')
def read_metingen():
    status = DataRepository.read_metingen()
    socketio.emit('B2F_metingen', {'metingen': status})

@socketio.on('F2B_read_latest_meting_per_id')
def read_latest_meting_per_id(apparaat_id):
    huidige_status = DataRepository.read_latest_meting_per_id(apparaat_id)
    socketio.emit('B2F_executed_device', {'meting': huidige_status})

@socketio.on('F2B_execute_device')
def execute_device(data):
    apparaat_id = data['apparaat_id']
    geforceerde_waarde = data['geforceerde_waarde']
    apparaat_waarde = 0
    huidige_status = DataRepository.read_latest_meting_per_id(apparaat_id)
    print(f'De actie voor apparaat {apparaat_id} wordt uitgevoerd')
    if apparaat_id == "TEM":
        tmp_waarde = tmp.lees_kanaal(0)
        apparaat_waarde = tmp.omzetten_naar_temperatuur(tmp_waarde,2)
    elif apparaat_id == "SER":
        if geforceerde_waarde == 0:
            if huidige_status['waarde'] == 0:
                apparaat_waarde = motor_open()
            else:
                apparaat_waarde = motor_close()
        else:
            if geforceerde_waarde == 1:
                apparaat_waarde = motor_open()
            if geforceerde_waarde == 2:
                apparaat_waarde = motor_close()
    elif apparaat_id == "HUM":
        while apparaat_waarde == 0:
            dht_waarde = instance.read()
            apparaat_waarde = dht_waarde.humidity
    elif (apparaat_id == "IR1" or apparaat_id == "IR2") and geforceerde_waarde == 0:
        apparaat_waarde = huidige_status['waarde'] + 1
    elif (apparaat_id == "IR1" or apparaat_id == "IR2") and geforceerde_waarde == 1:
        apparaat_waarde = 0
    tijdstip = datetime.datetime.now()
    nieuwe_waarde = DataRepository.add_meting(apparaat_id, tijdstip.strftime('%Y-%m-%d %H:%M:%S'), apparaat_waarde)
    nieuwe_waarde = DataRepository.read_latest_meting_per_id(apparaat_id)
    clear_display()
    if (apparaat_id == "SER"):
      if (nieuwe_waarde['waarde'] == 0):
        mijn_lcd.write_message(f"{apparaat_id}: Ontgrendeld", "2")
      else:
        mijn_lcd.write_message(f"{apparaat_id}: Vergrendeld", "2")
    else:
      mijn_lcd.write_message(f"{apparaat_id}: {nieuwe_waarde['waarde']} {nieuwe_waarde['eenheid']}", "2")
    socketio.emit('B2F_executed_device', {'meting': nieuwe_waarde})

@socketio.on('F2B_reboot')
def reboot():
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output)

@socketio.on('F2B_shutdown')
def shutdown():
    command = "/usr/bin/sudo /sbin/shutdown now"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output)

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')