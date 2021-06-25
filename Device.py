import logging
import threading
import time

__logger__ = logging.getLogger(__name__)

class Device(threading.Thread):
    def __init__(self, p_deviceName):
        threading.Thread.__init__(self)
        self.deamon = True
        self.status = True
        self.state = 0
        self.iter = 1
        self.execQ = list()
        self.inProgress = True

        self.DeviceName = p_deviceName

        self.objectCallback = None
        self.callback = None

        self.start()

    def getName(self):
        return self.DeviceName

    def getTextState(self):
        if self.getState() == 0:
            return "open"
        elif self.getState() == 100:
            return "close"
        elif self.getState() > 0 and self.getState() < 100:
            return "half-open"
        else:
            __logger__.error("State value should be in range 0 -100, not: " + str(self.getState()))
            return "idle"

    def setState(self, value : int):
        if isinstance(value, int):
            if value <= 100 and value >= 0:
                self.state = value
            else:
                __logger__.warning("Value should be in range 0 - 100, not: " + str(value))
        else:
            __logger__.error("Value type should be int, not: " + str(type(value)))

    def _increaseState(self, value : int):
        if isinstance(value, int):
            if value > 0:
                if value + self.getState() <= 100:
                    self.setState(value + self.getState())
                else:
                    self.setState(100)
            else:
                __logger__.error("Value type should be > 0, not: " + str(value))    
        else:
            __logger__.error("Value type should be int, not: " + str(type(value)))

    def _decreaseState(self, value : int):
        if isinstance(value, int):
            if value > 0:
                if self.getState() - value >= 0:
                    self.setState(self.getState() - value)
                else:
                    self.setState(0)
            else:
                __logger__.error("Value type should be > 0, not: " + str(value))    
        else:
            __logger__.error("Value type should be int, not: " + str(type(value)))

    def getState(self):
        return self.state

    def registerCallback(self, p_object):
        self.objectCallback = p_object

    def execCallback(self, value):
        self.objectCallback.updateValue(str(value) + " " + self.getTextState())

    def isCallback(self):
        if self.objectCallback != None:
            return True
        else:
            return False

    def stopProcess(self):
        self.inProgress = False

    def manualUp(self):
        self.stopProcess()
        self.execQ.append([self._decreaseState, 1])
        
    def manualDown(self):
        self.stopProcess()
        self.execQ.append([self._increaseState, 1])

    def autoUp(self):
        self.stopProcess()
        self.execQ.append([self._decreaseState, 0])

    def autoDown(self):
        self.stopProcess()
        self.execQ.append([self._increaseState, 100])

    def run(self):
        while self.status:
            if self.isCallback():
                self.execCallback(self.getState())
            time.sleep(0.1)
            if len(self.execQ) > 0:
                temp = self.execQ.pop(0)
                if temp[1] == 100 or temp[1] == 0:
                    self.inProgress = True
                    if temp[1] == 100:
                        while self.getState() < 100 and self.inProgress:
                            temp[0](self.iter)
                            self.execCallback(self.getState())
                            time.sleep(0.1)
                    elif temp[1] == 0:
                        while self.getState() > 0 and self.inProgress:
                            temp[0](self.iter)
                            self.execCallback(self.getState())
                            time.sleep(0.1)
                else:
                    temp[0](self.iter)
            time.sleep(0.1)
