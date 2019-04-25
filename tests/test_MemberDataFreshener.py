from drivers.Auth.MemberDataCacher import MemberDataCacher
from drivers.Auth.MemberDataFreshener import MemberDataFreshener
from drivers.DriverBase import DriverGroup
from drivers.Test.RunForSeconds import RunForSeconds
import json
from utils import get_cache_path
from utils.file_preserver import FilePreserver
import logging

def test_interval(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    mdc = root.add(MemberDataCacher('Member Data Cacher', None, None, None))
    mdf = root.add(MemberDataFreshener('Member Data Freshner', None, None, None))
    # fix dor = root.add(RunForSeconds(60.0*60.0))
    dor = root.add(RunForSeconds(10.0)) # rmv
    mdp1 = get_cache_path() / 'MemberData.json'
    mdp2 = get_cache_path() / 'MemberData.json.bak'
    with FilePreserver(mdp1, mdp2):
        assert not mdp1.exists()
        assert not mdp2.exists()
        root.setup()
        root.start()
        root.join()
        root.teardown()
        assert mdp1.exists()
        with mdp1.open('rt') as f:
            json.load(f)

