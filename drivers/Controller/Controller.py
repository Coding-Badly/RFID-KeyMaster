from drivers.DriverBase import DriverBaseOld
import queue


class Controller(DriverBaseOld):
    controller = "Controller"
    def __init__(self, config, loader):
        super().__init__(config, loader)
        self.controller = self.__class__.__name__
