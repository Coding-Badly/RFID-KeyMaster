from rfidkm.drivers.DriverBase import DriverBaseOld

class CurrentSense(DriverBaseOld):
    _events_ = ['current_change']

    def __init__(self, config):
        super().__init__(config)
        self.value = None

    def getValue(self):
        return self.value

