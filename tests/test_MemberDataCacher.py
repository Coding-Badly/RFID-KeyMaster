from drivers.Auth.MemberDataCacher import MemberDataCacher
from drivers.Auth.MemberDataFreshener import MemberDataFreshener
from drivers.DriverBase import DriverGroup
from drivers.Test.RunForSeconds import RunForSeconds
import json
from utils import get_cache_path
from utils.file_preserver import FilePreserver
import logging

logger = logging.getLogger(__name__)

def prepare_member_data_group(run_for_seconds = None):
    run_for_seconds = run_for_seconds if run_for_seconds else 60.0*60.0
    root = DriverGroup('root')
    mdc = root.add(MemberDataCacher('Member Data Cacher', None, None, None))
    mdf = root.add(MemberDataFreshener('Member Data Freshner', None, None, None))
    dor = root.add(RunForSeconds(run_for_seconds))
    mdp1 = mdc.get_path()
    mdp2 = mdp1.parent / (mdp1.name + '.bak')
    return (root, mdp1, mdp2)

def run_root(root):
    root.setup()
    root.start()
    root.join()
    root.teardown()

def test_interval(caplog):
    caplog.set_level(logging.INFO)
    logger.info('Part 1...')
    root, mdp1, mdp2 = prepare_member_data_group(10.0)
    with FilePreserver(mdp1, mdp2):
        assert not mdp1.exists()
        assert not mdp2.exists()
        run_root(root)
        assert mdp1.exists()
        logger.info('Part 2...')
        root, junk1, junk2 = prepare_member_data_group(10.0)
        run_root(root)
        assert mdp1.exists()
        assert mdp2.exists()

