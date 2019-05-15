from drivers.DriverBase import DriverBaseOld
import queue


class Controller(DriverBaseOld):
    controller = "Controller"
    def __init__(self, config):
        super().__init__(config)
        self.controller = self.__class__.__name__
