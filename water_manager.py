import time
import datetime
import RPi.GPIO as GPIO
import status
import sys
import os
import tailhead

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
history_filename = os.path.join(path, "history.txt")
settings_filename = os.path.join(path, "settings.txt")
events_filename = os.path.join(path, "events.txt")

autoIsOn = status.auto


def initialize():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(port_sensor_read, GPIO.IN)
    GPIO.setup(port_sensor_cmd, GPIO.OUT)
    GPIO.setup(port_pump_cmd, GPIO.OUT)


def checkIsWet():
    initialize()
    GPIO.output(port_sensor_cmd, GPIO.HIGH)
    time.sleep(2)
    value = GPIO.input(port_sensor_read) == 0
    GPIO.output(port_sensor_cmd, GPIO.LOW)
    writeHistory(value)
    status.last_reading = datetime.datetime.now()
    status.soil_was_wet = value
    status.save()
    GPIO.cleanup()
    return value


def turnOnPump():
    initialize()
    GPIO.output(port_pump_cmd, GPIO.HIGH)


def turnOffPump():
    initialize()
    GPIO.output(port_pump_cmd, GPIO.LOW)


def feed():
    writeLog(path, "INFO")
    turnOnPump()
    status.status = "FEEDING"
    status.save()
    writeLog("Watering for {0}s...".format(feed_duration), "INFO")
    time.sleep(feed_duration)
    turnOffPump()
    status.status = "PAUSE"
    status.last_watering = datetime.datetime.now()
    status.save()



def writeLog(message, errorLevel):
    line = str(datetime.datetime.now()) + "\t" + errorLevel + \
        "\t\t" + message + "\r\n"
    file = open(log_filename, 'a+')
    print(line)
    file.write(line)
    file.close()

def writeHistory(value):
    line = str(datetime.datetime.now())+"\t"+get_wet_dry(value)+"\r\n"
    file = open(history_filename, 'a+')
    file.write(line)
    file.close()


def get_wet_dry(isWet):
    return "WET" if isWet else "DRY"


def stopWork():
    GPIO.cleanup()
    autoIsOn = False
    status.auto = autoIsOn
    status.save()

def last_reads_are_dry(count):
    x = tailhead.tail(open(history_filename, 'rb'), count)
    dryCount = 0
    for i in x:
        if i.decode("utf-8").count("DRY")>0:
            dryCount += 1
    return dryCount == count

def shouldWork(isWet):
    result = False
    
    if not isWet:
        now = datetime.datetime.now()
        if (now.hour >= 19 and now.hour <=23) or (now.hour >= 3 and now.hour<=9):
            if last_reads_are_dry(5):
                result = True
    return result

def doWork():
    status.load()
    try:
        autoIsOn = status.auto
        isWet = checkIsWet()
        sw = shouldWork(isWet)
        s = "AUTO: {0}; SOIL: {1}; SHOULD_WORK: {2}".format(autoIsOn, get_wet_dry(isWet), sw)
        writeLog(s, "INFO" if isWet else "WARN")
        if sw:
            writeLog("Start watering.", "INFO")
            feed()
            isWet = checkIsWet()
            status.last_watering = datetime.datetime.now()
            status.soil_was_wet_after = isWet
            status.save()
            writeLog("After watering the soil is {0}.".format(get_wet_dry(isWet)), "INFO" if isWet else "ERROR")
    except KeyboardInterrupt:
        writeLog("Cleanup GPIO ports", "INFO")
        GPIO.cleanup()
        status.status = "SLEEPING"
        status.save()

if __name__ == '__main__':
    writeLog("Manager called from crontab", "INFO")
    writeLog(path, "INFO")
    doWork()