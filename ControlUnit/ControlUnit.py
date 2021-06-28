from PyQt5.QtWidgets import *
from PyQt5 import uic
import BAC0
import BAC0.core.devices.create_objects as CreateObj
import os, time
import threading
import requests
from requests.models import Response
import InternalClock

ControlUnitForm, _ = uic.loadUiType("ui/ControlUnitUi.ui")

class Mode:
    MANUAL = 1
    AUTO_BASIC = 2
    AUTO_EXTENDED = 3

class ControlUnitWindow(QDialog, ControlUnitForm, threading.Thread):
    def __init__(self, ip):
        super(ControlUnitWindow, self).__init__()
        threading.Thread.__init__(self)
        self.deamon = True
        self.setupUi(self)
        self.setWindowTitle("Control Unit")
        self.btn_autoBasic.clicked.connect(self.btnAutoBasic)
        self.btn_autoExtended.clicked.connect(self.btnAutoExtended)
        self.btn_manual.clicked.connect(self.btnManual)

        self.status = True

        self.bacnet = BAC0.connect(ip=ip, description="Control Unit")

        self.rollerShutters = None
        self.oneExecuteFlag = 0
        self.mode = Mode.MANUAL
        self.modeChanged = False
        self.initCounter = 0
        self.pingDevices = 0

        self.timetable = None
        self.actionsList = list()
        self.internalClock = InternalClock.InternalClock()
        self.internalClock.registerOutput(self)

        self.lastExecute = "idle"

        self.initDevices()

        self.start()

    def initDevices(self):
        self.rollerShutters = self.bacnet.whohas(object_name='get_mode#1')

    def btnAutoBasic(self):
        self.mode = Mode.AUTO_BASIC
        self.modeChanged = True
        self.timetable = None
        self.setModeInConnectedDevices()

    def btnAutoExtended(self):
        self.mode = Mode.AUTO_EXTENDED
        self.modeChanged = True
        self.setModeInConnectedDevices()

    def btnManual(self):
        self.mode = Mode.MANUAL
        self.modeChanged = True
        self.timetable = None
        self.setModeInConnectedDevices()


    def setTime(self, value : str):
        self.label_time.setText(value)

    def oneExecute(self, func):
        if self.oneExecuteFlag == 0:
            func()
            self.oneExecuteFlag = 1
 
    def setModeInConnectedDevices(self):
        for rs in self.rollerShutters:
            req = '{} multiStateValue 2 presentValue {} - 8'.format(rs[0], int(self.mode))
            self.bacnet.write(req, 842)

    def setStateInConnectedDevices(self, stateFlag): # True -> open, False -> close
        state = 0
        if stateFlag:
            state = 2
        else: 
            state = 3
        for rs in self.rollerShutters:
            req = '{} multiStateValue 4 presentValue {} - 8'.format(rs[0], int(state))
            self.bacnet.write(req, 842)

    def closeRollershutters(self):
        self.lastExecute = "close"
        self.setStateInConnectedDevices(False)

    def openRollershutters(self):
        self.lastExecute = "open"
        self.setStateInConnectedDevices(True)

    def deserializeTimetable(self):
        self.timetable = self.timetable["timetable"]

    def pingSerwer(self):
        try:
            requests.get('http://127.0.0.1:5000')
            return True
        except Exception:
            return False

    def doAction(self):
        if self.timetable:
            for act in self.timetable:
                if self.internalClock.isAfter(act["time"]):
                    if self.lastExecute != "open" and act["action"] == "open":
                        self.openRollershutters()
                    if self.lastExecute != "close" and act["action"] == "close":
                        self.closeRollershutters()

    def isDuskSensorAvaliable(self):
        duskSensor = self.bacnet.whohas(object_name='get_dusk#1')
        if len(duskSensor):
            return True
        else:
            return False

    def run(self):
        while self.status:
            if self.initCounter == 0:
                self.initDevices()      
                self.initCounter = 10
            else:
                self.initCounter -= 1    

            if self.pingDevices == 0:
                self.btn_autoExtended.setEnabled(self.pingSerwer())
                self.btn_autoBasic.setEnabled(self.isDuskSensorAvaliable())
                self.pingDevices = 10
            else:
                self.pingDevices -= 1

            if self.mode == Mode.AUTO_EXTENDED:
                if self.timetable == None:
                    self.timetable = requests.get('http://127.0.0.1:5000/api/get/timetable').json()
                    self.deserializeTimetable()
                self.doAction()
            time.sleep(0.1)

    def __del__(self):
        self.bacnet.disconnect()

class DeviceApp:
    def __init__(self):
        self.app = QApplication([])
        self.app.aboutToQuit.connect(self.myExitHandler)
        self.windowsContinter = list()

    def add(self, window):
        self.windowsContinter.append(window)

    def display(self):
        for dev in self.windowsContinter:
            dev.show()
        self.app.exec()

    def myExitHandler(self):
        for dev in self.windowsContinter:
            dev.__del__()
        os._exit(1)

#
# Zrobić żeby nie był dostępny tryb auto basic, jeżeli dusk sensor nie jest dostępny
# Podobnie z serwerem 
#