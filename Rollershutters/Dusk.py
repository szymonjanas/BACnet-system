from PyQt5.QtWidgets import *
from PyQt5 import uic
import BAC0
import BAC0.core.devices.create_objects as CreateObj

DuskForm, _ = uic.loadUiType("ui/dusk.ui")

class DuskState:
    DAY = 'day'
    NIGHT = 'night'

class DuskWindow(QDialog, DuskForm):
    def __init__(self, ip):
        super(DuskWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Dusk Sensor")
        self.btn_day.clicked.connect(self.btnDay)
        self.btn_night.clicked.connect(self.btnNight)

        self.duskState = DuskState.DAY

        self.bacnet = BAC0.connect(ip=ip, description="Dusk sensor (Day/Night)")
        self.bacnet.this_application.add_object(
            CreateObj.create_MV(oid=1, pv=1, name='get_dusk#{}'.format(1), states=['day', 'night'], pv_writable=True))
        self.get_state = self.bacnet.this_application.get_object_name('get_dusk#1')

    def btnDay(self):
        self.duskState = DuskState.DAY
        self.setState(self.duskState)
        self.get_state.WriteProperty('presentValue', 1)

    def btnNight(self):
        self.duskState = DuskState.NIGHT
        self.setState(self.duskState)
        self.get_state.WriteProperty('presentValue', 2)

    def setState(self, state : DuskState):
        self.label_state.setText(str(state))

    
