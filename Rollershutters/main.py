import logging
import Gui
import Device
import Network
import Dusk 

logging.basicConfig(filename='bacnet.log', level=logging.DEBUG)
__logger__ = logging.getLogger(__name__)

dev = Device.Device("sterownik 01")
net = Network.Network(Network.DeviceDetails('127.0.0.2/8', "sterownik 01"), dev)
dev2 = Device.Device("sterownik 02")
net = Network.Network(Network.DeviceDetails('127.0.0.3/8', "sterownik 02"), dev2)
app = Gui.DeviceApp()
app.create(dev)
app.create(dev2)
app.add(Dusk.DuskWindow('127.0.0.4/8'))
app.display()
