from drivers.DriverBase import DriverGroup, DeathOfRats
from drivers.Test.Ping import Ping1, Ping2
from drivers.Test.Pong import Pong1
from drivers.Test.RunForSeconds import RunForSeconds
import logging
import time

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
    tm2 = tm1.add(Ping1())
    tm3 = tm1.add(Pong1())
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
    tm2 = tm1.add(Ping1())
    tm3 = tm1.add(Pong1())
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
    lft_ping = lft.add(Ping1())
    lft_pong = lft.add(Pong1())
    rgt = root.add(DriverGroup('right'))
    rgt_pong = rgt.add(Pong1())
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
    lft_lft_ping = lft_lft.add(Ping1())
    lft_lft_pong = lft_lft.add(Pong1())
    lft_rgt_ping = lft_rgt.add(Ping1())
    lft_rgt_pong = lft_rgt.add(Pong1())
    rgt_lft_ping = rgt_lft.add(Ping1())
    rgt_lft_pong = rgt_lft.add(Pong1())
    #
    rgt_rgt_pong = rgt_rgt.add(Pong1())
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
    lft_lft_ping = lft_lft.add(Ping1())
    rgt_rgt_pong = rgt_rgt.add(Pong1())
    assert lft_lft_ping == rgt_rgt_pong.find_driver_by_name('Ping1')
    assert rgt_rgt_pong == lft_lft_ping.find_driver_by_name('Pong1')
    assert lft_lft_ping == rgt_rgt_pong.find_driver_by_event('receive_ball')
    assert rgt_rgt_pong == lft_lft_ping.find_driver_by_event('receive_ball')

def test_ping_pong_run_1(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    ping = root.add(Ping1())
    pong = root.add(Pong1())
    root.setup()
    root.start()
    ping.join()
    pong.join()
    root.teardown()
    assert ping._last_count == 1000
    assert pong._last_count == 999

def x_test_RunForSeconds_simple_test(caplog):
    root = DriverGroup('root')
    tm1 = root.add(RunForSeconds(1.0))
    root.setup()
    root.start()
    tm1.join()
    root.teardown()

def test_one_second_of_ping_pong_1(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    tm1 = root.add(RunForSeconds(1.0))
    tm2 = root.add(Ping1(False))
    tm3 = root.add(Pong1())
    root.setup()
    root.start()
    tm1.join()
    tm2.join()
    tm3.join()
    root.teardown()
    logging.info(tm2._last_count)
    logging.info(tm3._last_count)

def test_one_second_of_ping_pong_2(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    rfs = root.add(RunForSeconds(1.0))
    ping = root.add(Ping2())
    pong = root.add(Pong1())
    root.setup()
    root.start()
    rfs.join()
    ping.join()
    pong.join()
    root.teardown()
    assert ping._last_count == 1000
    assert pong._last_count == 999

def test_DeathOfRats(caplog):
    caplog.set_level(logging.INFO)
    root = DriverGroup('root')
    dor = root.add(DeathOfRats(name='DeathOfRats', config=None, loader=None, id=None))
    ping = root.add(Ping2())
    pong = root.add(Pong1())
    root.setup()
    root.start()
    time.sleep(1.0)
    dor.stop_all()
    dor.join()
    # rmv logging.info('dor.join')
    ping.join()
    # rmv logging.info('ping.join')
    pong.join()
    # rmv logging.info('pong.join')
    root.teardown()
    assert ping._last_count == 1000
    assert pong._last_count == 999

    #tm1.setup()
    #tm1.start()
    #tm2.join()
    #tm3.join()
    #assert tm2._last_count == 1000
    #assert tm3._last_count == 999
#    rgt_ping = lft.add(Ping1())
#startable = list()
#tm1 = Ping1()
#if tm1.setup():
#    startable.append(tm1)

