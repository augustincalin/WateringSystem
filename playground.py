import RPi.GPIO as GPIO
import time
import datetime

port_sensor_read = 18
port_sensor_cmd = 23
port_pump_cmd = 25

def initialize():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(port_sensor_read, GPIO.IN)
    GPIO.setup(port_sensor_cmd, GPIO.OUT)
    GPIO.setup(port_pump_cmd, GPIO.OUT)


def check():
    initialize()
    GPIO.output(port_sensor_cmd, GPIO.HIGH)
    time.sleep(10)
    wetCount = 0
    for x in range(0,100):
        time.sleep(2)
        value = GPIO.input(port_sensor_read) == 0
        if value == True:
            wetCount += 1
    print(wetCount)
    value = wetCount > 70
    GPIO.output(port_sensor_cmd, GPIO.LOW)
    GPIO.cleanup()
    return value