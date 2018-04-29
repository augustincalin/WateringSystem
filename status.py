import pickle
import os.path
import datetime
import sys

path = sys.path[0]
status_file = os.path.join(path, "status.bin")

class Status:
    auto = True
    feed_duration = 60
    feed_pause = 30
    feed_iterations = 5
    status = "PAUSE"
    last_watering = datetime.datetime.now()
    soil_was_wet_after = False
    last_reading = datetime.datetime.now()
    soil_was_wet = False

    def __init__(self):
        if os.path.isfile(status_file):
            self.load()
        else:
            self.auto = True
            self.feed_duration = 60
            self.feed_pause = 30
            self.feed_iterations = 5
            self.status = "PAUSE"
            self.last_watering = datetime.datetime.now()
            self.soil_was_wet_after = False
            self.last_reading = datetime.datetime.now()
            self.soil_was_wet = False
            self.save()


    def save(self):
        pickle.dump(self, open(status_file,'wb'))


    def load(self):
        value = pickle.load(open(status_file, 'rb'))
        self.auto = value.auto
        self.feed_duration = value.feed_duration
        self.feed_iterations = value.feed_iterations
        self.feed_pause = value.feed_pause
        self.last_reading = value.last_reading
        self.last_watering = value.last_watering
        self.soil_was_wet = value.soil_was_wet
        self.soil_was_wet_after = value.soil_was_wet_after
        self.status = value.status


