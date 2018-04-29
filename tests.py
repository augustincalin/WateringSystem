import time
import datetime
import RPi.GPIO as GPIO

# settings
port_sensor_read = 18
port_sensor_cmd = 23
port_pump_cmd = 25

def initialize():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(port_sensor_read, GPIO.IN)
    GPIO.setup(port_sensor_cmd, GPIO.OUT)
    GPIO.setup(port_pump_cmd, GPIO.OUT)


def checkIsWet():
    GPIO.output(port_sensor_cmd, GPIO.HIGH)
    time.sleep(1)
    value = GPIO.input(port_sensor_read) == 0
    GPIO.output(port_sensor_cmd, GPIO.LOW)
    return value


def doWork():
    initialize()
    print(checkIsWet())
    GPIO.cleanup()


def startPump():
    initialize()
    print('Pump ON')
    GPIO.output(port_pump_cmd, GPIO.HIGH)


def stopPump():
    initialize()
    GPIO.output(port_pump_cmd, GPIO.LOW)
    print('Pump OFF')
    GPIO.cleanup()
    

