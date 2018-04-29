import time
import datetime
import RPi.GPIO as GPIO
import status

status = status.Status()

# settings
port_sensor_read = 18
port_sensor_cmd = 23
port_pump_cmd = 25

feed_duration = status.feed_duration
feed_pause = status.feed_pause
feed_iterations = status.feed_iterations

log_filename = "log.txt"
settings_filename = "settings.txt"
events_filename = "events.txt"

shouldWork = status.auto


def initialize():
    print("init")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(port_sensor_read, GPIO.IN)
    GPIO.setup(port_sensor_cmd, GPIO.OUT)
    GPIO.setup(port_pump_cmd, GPIO.OUT)


def checkIsWet():
    initialize()
    writeLog("Sensor ON", "INFO")
    GPIO.output(port_sensor_cmd, GPIO.HIGH)
    time.sleep(1)
    writeLog("Read Sensor", "INFO")
    value = GPIO.input(port_sensor_read) == 0
    writeLog("Sensor OFF", "INFO")
    GPIO.output(port_sensor_cmd, GPIO.LOW)
    writeLog("Value read: {0}".format(value), "INFO")
    status.last_reading = datetime.datetime.now()
    status.soil_was_wet = value
    return value


def turnOnPump():
    initialize()
    writeLog("Pump ON", "INFO")
    GPIO.output(port_pump_cmd, GPIO.HIGH)


def turnOffPump():
    initialize()
    writeLog("Pump OFF", "INFO")
    GPIO.output(port_pump_cmd, GPIO.LOW)


def feed():
    writeLog("Turn ON pump", "INFO")
    turnOnPump()
    status.status = "FEEDING"
    status.save()
    writeLog("Feeding for {0}s...".format(feed_duration), "INFO")
    time.sleep(feed_duration)
    writeLog("Turn OFF pump", "INFO")
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
            while not isWet and counter <= feed_iterations:
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
            writeLog("AUTO is off", "INFO")
    except KeyboardInterrupt:
        writeLog("Cleanup GPIO ports", "INFO")
        GPIO.cleanup()
        status.status = "SLEEPING"
        status.save()

if __name__ == '__main__':
    writeLog("STARTING MANAGER...", "INFO")
    doWork()
