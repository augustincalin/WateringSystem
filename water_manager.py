import time
import datetime
import RPi.GPIO as GPIO
import status
import sys
import os

status = status.Status()
path = sys.path[0]
# settings
port_sensor_read = 18
port_sensor_cmd = 23
port_pump_cmd = 25

feed_duration = status.feed_duration
feed_pause = status.feed_pause
feed_iterations = status.feed_iterations

log_filename = os.path.join(path, "log.txt")
settings_filename = os.path.join(path, "settings.txt")
events_filename = os.path.join(path, "events.txt")

shouldWork = status.auto


def initialize():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(port_sensor_read, GPIO.IN)
    GPIO.setup(port_sensor_cmd, GPIO.OUT)
    GPIO.setup(port_pump_cmd, GPIO.OUT)


def checkIsWet():
    initialize()
    GPIO.output(port_sensor_cmd, GPIO.HIGH)
    time.sleep(1)
    wetCount = 0
    for x in range(0,100):
        value = GPIO.input(port_sensor_read) == 0
        if value == True:
            wetCount += 1
    value = wetCount > 70
    GPIO.output(port_sensor_cmd, GPIO.LOW)
    writeLog("WET readings {1} / 100. Is WET?: {0}".format(value, wetCount), "INFO")
    status.last_reading = datetime.datetime.now()
    status.soil_was_wet = value
    GPIO.cleanup()
    return value


def turnOnPump():
    initialize()
    GPIO.output(port_pump_cmd, GPIO.HIGH)


def turnOffPump():
    initialize()
    GPIO.output(port_pump_cmd, GPIO.LOW)


def feed():
    turnOnPump()
    status.status = "FEEDING"
    status.save()
    writeLog("Feeding for {0}s...".format(feed_duration), "INFO")
    time.sleep(feed_duration)
    turnOffPump()
    status.status = "PAUSE"
    status.save()
    writeLog("Pause for {0}s...".format(feed_pause), "INFO")
    time.sleep(feed_pause)


def writeLog(message, errorLevel):
    line = str(datetime.datetime.now()) + "\t" + errorLevel + \
        "\t\t" + message + "\r\n"
    file = open(log_filename, 'a+')
    print(line)
    file.write(line)
    file.close()


def stopWork():
    GPIO.cleanup()
    shouldWork = False

def doWork():
    status.load()
    writeLog("START", "INFO")
    try:
        shouldWork = status.auto
        if shouldWork:
            counter = 1
            isWet = checkIsWet()
            writeLog("Soil is wet? {0}".format(isWet), "INFO" if isWet else "WARN")
            while not isWet and counter <= feed_iterations and shouldWork:
                writeLog("Feeding START #{0}/{1}".format(counter, feed_iterations), "INFO")
                feed()
                status.last_watering = datetime.datetime.now()
                status.save()
                writeLog("Feeding END #{0}".format(counter), "INFO")
                isWet = checkIsWet()
                status.soil_was_wet_after = isWet
                status.save()

                writeLog("Soil is still dry? {0}".format(not isWet), "INFO" if isWet else "WARN")
                counter += 1
            if not isWet:
                writeLog("After {0} feeding cycles the soil is still dry. Check the water level in tank!".format(feed_iterations), "ERROR")
        else:
            writeLog("AUTO is off, no action", "INFO")
    except KeyboardInterrupt:
        writeLog("Cleanup GPIO ports", "INFO")
        GPIO.cleanup()
        status.status = "SLEEPING"
        status.save()

if __name__ == '__main__':
    writeLog("STARTING MANAGER...", "INFO")
    doWork()