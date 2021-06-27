import time, threading


class InternalClock(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.deamon = True
        self.hours = 0
        self.minutes = 0
        self.timesFaster = 60
        self.hoursTolerance = 3

        self.clockRun = True

        self.outputObject = None

        self.start()

    def registerOutput(self, output):
        self.outputObject = output
    
    def displayTime(self):
        if self.outputObject:
            self.outputObject.setTime(self.getTextTime())

    def getTextTime(self):
        min = "{}".format(self.minutes)
        if self.minutes < 10:
            min = "0{}".format(self.minutes)
        hor = "{}".format(self.hours)
        if self.hours < 10:
            hor = "0{}".format(self.hours)
        return "{}:{}".format(hor, min)

    def setHours(self, value):
        if value >= 0 and value < 24:
            self.hours = value

    def setMinutes(self, value):
        if value >= 0 and value < 60:
            self.minutes = value

    def incrementMinutes(self):
        self.minutes += 1
        if self.minutes > 60:
            self.minutes = 0
            self.hours += 1
            if self.hours > 24:
                self.hours = 0

    def getHours(self):
        return self.hours

    def getMinutes(self):
        return self.minutes

    def __del__(self):
        self.clockRun = False

    def isAfter(self, value):
        valueHours = int(value[:2])
        valueMinutes = int(value[3:])
        if valueHours < self.hours:
            if self.hours - valueHours < self.hoursTolerance:
                return True
            else:
                return False
        if valueHours == self.hours:
            if valueMinutes < self.minutes:
                return True
            else:
                return False
        else:
            return False

    def run(self):
        while self.clockRun:
            self.incrementMinutes()
            self.displayTime()
            time.sleep(1/self.timesFaster)
    