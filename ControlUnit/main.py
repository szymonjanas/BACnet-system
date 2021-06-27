import ControlUnit


app = ControlUnit.DeviceApp()
app.add(ControlUnit.ControlUnitWindow('127.0.0.15/8'))

app.display()
