import logging
import Device
from PyQt5.QtWidgets import *
from PyQt5 import uic
import os

__logger__ = logging.getLogger(__name__)

DeviceForm, _ = uic.loadUiType("ui/deviceUi.ui")

class DeviceWindow(QDialog, DeviceForm):
    def __init__(self, p_device : Device.Device):
        super(DeviceWindow, self).__init__()
        self.device = p_device
        self.device.registerCallback(self)
        self.setupUi(self)
        self.setWindowTitle(self.device.getName())
        self.label_name.setText(self.device.getName())

        self.btn_close.clicked.connect(self.btnClose)
        self.btn_open.clicked.connect(self.btnOpen)
        self.btn_up.clicked.connect(self.btnUp)
        self.btn_down.clicked.connect(self.btnDown)

    def updateValue(self, value):
        self.label_state.setText(str(value))

    def btnOpen(self):
        self.device.autoUp()

    def btnClose(self):
        self.device.autoDown()

    def btnUp(self):
        self.device.manualUp()

    def btnDown(self):
        self.device.manualDown()

class DeviceApp:
    def __init__(self):
        self.app = QApplication([])
        self.app.aboutToQuit.connect(self.myExitHandler)
        self.windowsContinter = list()

    def create(self, p_device):
        self.windowsContinter.append(DeviceWindow(p_device))

    def display(self):
        for dev in self.windowsContinter:
            dev.show()
        self.app.exec()

    def myExitHandler(self):
        os._exit(1)
