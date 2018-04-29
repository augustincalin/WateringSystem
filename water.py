# External module imp
import RPi.GPIO as GPIO
import datetime
import time

init = False

GPIO.setmode(GPIO.BCM)

def getLastWatered():
    try:
        f = open("last_watered.txt", "r")
        return f.readline()
    except:
        return "NEVER"

def getStatus(pin = 8):
    GPIO.setup(pin, GPIO.IN)
    return GPIO.input(pin)

def initOutput(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    GPIO.output(pin, GPIO.HIGH)

def pumpOn(pin=7, delay=1):
    initOutput(pin)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(delay)
    GPIO.output(pin, GPIO.HIGH)
    f = open("last_watered.txt", "w")
    f.write("Last watered {}".format(datetime.datetime.now()))
    f.close()


def autoWater(delay = 5, pumpPin = 7, sensorPin = 8):
    waterCount = 0
    initOutput(pumpPin)
    try:
        while waterCount < 10:
            time.sleep(delay)
            isWet = getStatus(sensorPin) == 0
            if isWet:
                waterCount = 0
            else:
                if waterCount < 5:
                    pumpOn(pumpPin, 1)
                waterCount+=1
    except KeyboardInterrupt:
        GPIO.cleanup()