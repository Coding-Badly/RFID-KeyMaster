import logging
import time

from rfidkm.drivers.DriverBase import DriverGroup, DeathOfRats
from rfidkm.drivers.Test.Ping import Ping1, Ping2
from rfidkm.drivers.Test.Pong import Pong1
from rfidkm.drivers.Test.RunForSeconds import RunForSeconds

def test_DriverGroup_simple_construction():
    tm1 = DriverGroup()
    assert tm1.name.startswith('whatever #')
    tm1 = DriverGroup('default')
    assert tm1.name == 'default'

def rmv_test_empty():
    tm1 = DriverGroup()
    tm1.setup()
    tm1.start()

def rmv_test_just_one():
    tm1 = DriverGroup()
    tm2 = Ping1()
    tm1.add(tm2)
    assert tm1['Ping1'] == tm2
    tm3 = tm2.find_driver_by_name('Ping1')
    assert tm3 == tm2
    tm1.setup()
    tm1.start()
    assert tm2.is_alive()

def test_ping_pong_by_driver_name(caplog):
    caplog.set_level(logging.INFO)
    tm1 = DriverGroup()
    tm2 = tm1.add(Ping1(None))
    tm3 = tm1.add(Pong1(None))
    assert tm1['Ping1'] == tm2
    assert tm1['Pong1'] == tm3
    assert tm2 == tm1.find_driver_by_name('Ping1')
    assert tm2 == tm2.find_driver_by_name('Ping1')
    assert tm2 == tm3.find_driver_by_name('Ping1')
    assert tm3 == tm1.find_driver_by_name('Pong1')
    assert tm3 == tm2.find_driver_by_name('Pong1')
    assert tm3 == tm3.find_driver_by_name('Pong1')

def test_ping_pong_by_event_name(caplog):
    caplog.set_level(logging.INFO)
    tm1 = DriverGroup()
    tm2 = tm1.add(Ping1(None))
    tm3 = tm1.add(Pong1(None))
    assert tm3 == tm2.find_driver_by_event('receive_ball')
    assert tm2 == tm3.find_driver_by_event('receive_ball')
    assert tm2 == tm1.find_driver_by_event('receive_ball')
    assert tm1.find_driver_by_event('bad_news') == None
    assert tm2.find_driver_by_event('bad_news') == None
    assert tm3.find_driver_by_event('bad_news') == None

def test_ping_pong_level_two_tree(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    lft = root.add(DriverGroup('left'))
    lft_ping = lft.add(Ping1(None))
    lft_pong = lft.add(Pong1(None))
    rgt = root.add(DriverGroup('right'))
    rgt_pong = rgt.add(Pong1(None))
    assert lft == root.find_driver_by_name('left')
    assert lft == lft.find_driver_by_name('left')
    assert lft == rgt.find_driver_by_name('left')
    assert lft == lft_ping.find_driver_by_name('left')
    assert lft == lft_pong.find_driver_by_name('left')
    assert lft == rgt_pong.find_driver_by_name('left')
    assert rgt == root.find_driver_by_name('right')
    assert rgt == lft.find_driver_by_name('right')
    assert rgt == rgt.find_driver_by_name('right')
    assert rgt == lft_ping.find_driver_by_name('right')
    assert rgt == lft_pong.find_driver_by_name('right')
    assert rgt == rgt_pong.find_driver_by_name('right')
    assert root == root.find_driver_by_name('root')
    assert lft_ping == rgt_pong.find_driver_by_name('Ping1')
    assert lft_pong == lft_ping.find_driver_by_name('Pong1')
    assert lft_ping == rgt_pong.find_driver_by_event('receive_ball')
    assert lft_ping == lft_pong.find_driver_by_event('receive_ball')
    assert lft_pong == lft_ping.find_driver_by_event('receive_ball')
    assert root.find_driver_by_event('bad_news') == None
    assert lft_ping.find_driver_by_event('bad_news') == None
    assert lft_pong.find_driver_by_event('bad_news') == None
    assert rgt_pong.find_driver_by_event('bad_news') == None

def test_ping_pong_level_three_tree(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    lft = root.add(DriverGroup('left'))
    lft_lft = lft.add(DriverGroup('left-left'))
    lft_rgt = lft.add(DriverGroup('left-right'))
    rgt = root.add(DriverGroup('right'))
    rgt_lft = rgt.add(DriverGroup('right-left'))
    rgt_rgt = rgt.add(DriverGroup('right-right'))
    lft_lft_ping = lft_lft.add(Ping1(None))
    lft_lft_pong = lft_lft.add(Pong1(None))
    lft_rgt_ping = lft_rgt.add(Ping1(None))
    lft_rgt_pong = lft_rgt.add(Pong1(None))
    rgt_lft_ping = rgt_lft.add(Ping1(None))
    rgt_lft_pong = rgt_lft.add(Pong1(None))
    #
    rgt_rgt_pong = rgt_rgt.add(Pong1(None))
    assert lft_lft_ping == lft_lft_pong.find_driver_by_name('Ping1')
    assert lft_lft_pong == lft_lft_ping.find_driver_by_name('Pong1')
    assert lft_rgt_ping == lft_rgt_pong.find_driver_by_name('Ping1')
    assert lft_rgt_pong == lft_rgt_ping.find_driver_by_name('Pong1')
    assert rgt_lft_ping == rgt_lft_pong.find_driver_by_name('Ping1')
    assert rgt_lft_pong == rgt_lft_ping.find_driver_by_name('Pong1')
    assert rgt_lft_ping == rgt_rgt_pong.find_driver_by_name('Ping1')
    assert lft_lft_ping == lft_lft_pong.find_driver_by_event('receive_ball')
    assert lft_lft_pong == lft_lft_ping.find_driver_by_event('receive_ball')
    assert lft_rgt_ping == lft_rgt_pong.find_driver_by_event('receive_ball')
    assert lft_rgt_pong == lft_rgt_ping.find_driver_by_event('receive_ball')
    assert rgt_lft_ping == rgt_lft_pong.find_driver_by_event('receive_ball')
    assert rgt_lft_pong == rgt_lft_ping.find_driver_by_event('receive_ball')
    assert rgt_lft_ping == rgt_rgt_pong.find_driver_by_event('receive_ball')

def test_ping_pong_level_three_sparse(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    lft = root.add(DriverGroup('left'))
    lft_lft = lft.add(DriverGroup('left-left'))
    lft_rgt = lft.add(DriverGroup('left-right'))
    rgt = root.add(DriverGroup('right'))
    rgt_lft = rgt.add(DriverGroup('right-left'))
    rgt_rgt = rgt.add(DriverGroup('right-right'))
    lft_lft_ping = lft_lft.add(Ping1(None))
    rgt_rgt_pong = rgt_rgt.add(Pong1(None))
    assert lft_lft_ping == rgt_rgt_pong.find_driver_by_name('Ping1')
    assert rgt_rgt_pong == lft_lft_ping.find_driver_by_name('Pong1')
    assert lft_lft_ping == rgt_rgt_pong.find_driver_by_event('receive_ball')
    assert rgt_rgt_pong == lft_lft_ping.find_driver_by_event('receive_ball')

def test_ping_pong_run_1(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    ping = root.add(Ping1(None))
    pong = root.add(Pong1(None))
    root.setup()
    root.start()
    # rmv ping.join()
    # rmv pong.join()
    root.join()
    root.teardown()
    assert ping._last_count == 1000
    assert pong._last_count == 999

def x_test_RunForSeconds_simple_test(caplog):
    root = DriverGroup('root')
    tm1 = root.add(RunForSeconds({'seconds':1.0}))
    root.setup()
    root.start()
    tm1.join()
    root.teardown()

def test_one_second_of_ping_pong_1(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    tm1 = root.add(RunForSeconds({'seconds':1.0}))
    tm2 = root.add(Ping1({'stop_at_1000':False}))
    tm3 = root.add(Pong1(None))
    root.setup()
    root.start()
    # rmv tm1.join()
    # rmv tm2.join()
    # rmv tm3.join()
    root.join()
    root.teardown()
    logging.info(tm2._last_count)
    logging.info(tm3._last_count)

def test_one_second_of_ping_pong_2(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    rfs = root.add(RunForSeconds({'seconds':1.0}))
    ping = root.add(Ping2(None))
    pong = root.add(Pong1(None))
    root.setup()
    root.start()
    # rmv rfs.join()
    # rmv ping.join()
    # rmv pong.join()
    root.join()
    root.teardown()
    assert ping._last_count == 1000
    assert pong._last_count == 999

def test_DeathOfRats(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    dor = root.add(DeathOfRats(None))
    ping = root.add(Ping2(None))
    pong = root.add(Pong1(None))
    root.setup()
    root.start()
    time.sleep(1.0)
    dor.stop_all()
    # rmv dor.join()
    # rmv logging.info('dor.join')
    # rmv ping.join()
    # rmv logging.info('ping.join')
    # rmv pong.join()
    # rmv logging.info('pong.join')
    root.join()
    root.teardown()
    assert ping._last_count == 1000
    assert pong._last_count == 999

def test_flatten_1(caplog):
    root = DriverGroup('root')
    assert root.flatten() == []

def test_flatten_2(caplog):
    root = DriverGroup('root')
    lft = root.add(DriverGroup('left'))
    lft_ping = lft.add(Ping1(None))
    lft_pong = lft.add(Pong1(None))
    rgt = root.add(DriverGroup('right'))
    rgt_pong = rgt.add(Pong1(None))
    assert root.flatten() == [lft_ping, lft_pong, rgt_pong]

def test_flatten_3(caplog):
    root = DriverGroup('root')
    lft = root.add(DriverGroup('left'))
    lft_lft = lft.add(DriverGroup('left-left'))
    lft_rgt = lft.add(DriverGroup('left-right'))
    rgt = root.add(DriverGroup('right'))
    rgt_lft = rgt.add(DriverGroup('right-left'))
    rgt_rgt = rgt.add(DriverGroup('right-right'))
    lft_lft_ping = lft_lft.add(Ping1(None))
    lft_lft_pong = lft_lft.add(Pong1(None))
    lft_rgt_ping = lft_rgt.add(Ping1(None))
    lft_rgt_pong = lft_rgt.add(Pong1(None))
    rgt_lft_ping = rgt_lft.add(Ping1(None))
    rgt_lft_pong = rgt_lft.add(Pong1(None))
    #rgt_rgt_ping = rgt_rgt.add(Ping1(None))
    rgt_rgt_pong = rgt_rgt.add(Pong1(None))
    assert root.flatten() == [lft_lft_ping, lft_lft_pong, lft_rgt_ping, lft_rgt_pong, rgt_lft_ping, rgt_lft_pong, rgt_rgt_pong]

