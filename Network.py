import threading
import time
import BAC0
import BAC0.core.devices.create_objects as CreateObj
import Device

class DeviceDetails:
    def __init__(self, 
                    ip, 
                    description = "This is Rollershutter device!"):
        self.ip = ip
        self.description = description

class Network(threading.Thread):
    def __init__(self, p_details : DeviceDetails, p_device : Device.Device):
        threading.Thread.__init__(self)
        self.deamon = True
        self.status = True
        self.device = p_device
        self.bacnet = BAC0.connect(ip=p_details.ip, description=p_details.description)

        self.create()
        self.get_mode = self.bacnet.this_application.get_object_name('get_mode#1')
        self.set_mode = self.bacnet.this_application.get_object_name('set_mode#2')
        self.get_state = self.bacnet.this_application.get_object_name('get_state#3')
        self.set_state = self.bacnet.this_application.get_object_name('set_state#4')

        self.syncStates()

        self.device.registerModeChange(self)

        self.start()

    def __del__(self):
        self.bacnet.disconnect()

    def create(self):
        self.bacnet.this_application.add_object(
            CreateObj.create_MV(oid=1, pv=1, name='get_mode#{}'.format(1), states=['manual', 'auto_basic', 'auto_extended'], pv_writable=True))
        self.bacnet.this_application.add_object(
            CreateObj.create_MV(oid=2, pv=1, name='set_mode#{}'.format(2), states=['manual', 'auto_basic', 'auto_extended'], pv_writable=True))
        self.bacnet.this_application.add_object(
            CreateObj.create_MV(oid=3, pv=1, name='get_state#{}'.format(3), states=['idle', 'open', 'close', 'half-open'], pv_writable=True))
        self.bacnet.this_application.add_object(
            CreateObj.create_MV(oid=4, pv=1, name='set_state#{}'.format(4), states=['idle', 'open', 'close'], pv_writable=True))

    def syncStates(self):
        stateText = self.device.getTextState()
        if stateText == 'open':
            self.get_state.WriteProperty('presentValue', 2)
        elif stateText == 'close':
            self.get_state.WriteProperty('presentValue', 3)
        elif stateText == 'half-open':
            self.get_state.WriteProperty('presentValue', 4)
       
    def modeChange(self, value):
        self.device.setMode(value)
        self.get_mode.WriteProperty('presentValue', value)
        self.set_mode.WriteProperty('presentValue', value)

    def autoExtOpen(self):
        self.device.auto_extended()
        self.device.autoUp()

    def autoExtClose(self):
        self.device.auto_extended()
        self.device.autoDown()

    def autoBasicOpen(self):
        self.device.auto_basic()
        self.device.autoUp()

    def autoBasicClose(self):
        self.device.auto_basic()
        self.device.autoDown()     

    def run(self):
        while self.status:
            mode = self.set_mode.ReadProperty('presentValue')
            if mode != self.device.getMode():
                self.modeChange(mode)
            
            if mode == 3:
                reqState = self.set_state.ReadProperty('presentValue')
                self.set_state.WriteProperty('presentValue', 1)
                reqStatesText = self.set_state.ReadProperty('stateText')
                if reqState != 1:
                    if reqStatesText[reqState] != self.device.getTextState():
                        if reqState == 2 and self.device.getExecution() != Device.Execution.OPENING:
                            self.autoExtOpen()
                        if reqState == 3 and self.device.getExecution() != Device.Execution.CLOSING:
                            self.autoExtClose()

            if mode == 2:
                duskSensor = self.bacnet.whohas(object_name='get_dusk#1')
                duskValue = self.bacnet.read('{} 19 1 presentValue'.format(duskSensor[0][0]))
                duskValuesText = self.bacnet.read('{} 19 1 stateText'.format(duskSensor[0][0]))
                if duskValuesText[duskValue-1] == 'day':
                    if self.device.getTextState() != "open" and self.device.getExecution() != Device.Execution.OPENING:    
                        self.autoExtOpen()
                if duskValuesText[duskValue-1] == 'night':
                    if self.device.getTextState() != "close" and self.device.getExecution() != Device.Execution.CLOSING:    
                        self.autoExtClose()

            self.syncStates()
            time.sleep(0.1)
