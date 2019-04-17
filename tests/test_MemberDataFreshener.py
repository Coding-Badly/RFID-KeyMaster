from drivers.Auth.MemberDataCacher import MemberDataCacher
from drivers.Auth.MemberDataFreshener import MemberDataFreshener
from drivers.DriverBase import DriverGroup, DeathOfRats
from drivers.Test.RunForSeconds import RunForSeconds
import logging
import time

def test_interval(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    mdc = root.add(MemberDataCacher('Member Data Cacher', None, None, None))
    mdf = root.add(MemberDataFreshener('Member Data Freshner', None, None, None))
    # fix dor = root.add(RunForSeconds(60.0*60.0))
    dor = root.add(RunForSeconds(10.0)) # rmv
    root.setup()
    root.start()
    root.join()
    root.teardown()

