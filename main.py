import logging
import Gui
import Device
import time 

logging.basicConfig(filename='bacnet.log', level=logging.DEBUG)
__logger__ = logging.getLogger(__name__)

dev = Device.Device("sterownik 01")
dev2 = Device.Device("sterownik 02")
app = Gui.DeviceApp()
app.create(dev)
app.create(dev2)
app.display()
