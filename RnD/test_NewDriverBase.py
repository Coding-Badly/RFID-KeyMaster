import logging

from NewDriverBase import DriverBase

def rmv_test_001(caplog):
    caplog.set_level(logging.INFO)
    tm1 = DriverBase()
    tm1.setup()
    tm1.start_and_wait()
    tm1.join()
    assert tm1._thread is None
    tm1.start_and_wait()
    tm1.join()
    assert tm1._thread is None
