import logging
from threading import Thread, Event, Lock, get_ident
from time import sleep

logger = logging.getLogger(__name__)

class DriverBase():

    # Called by DriverGroup after loading before starting
    # Presumed to only ever be called once
    def setup(self):
        self._lock = Lock()
        self._thread = None

    def teardown(self):
        #self._thread = None  # rmv? keep? protect?
        pass

    # Called from DriverGroup.start
    def start_and_wait(self):
        logger.info("{:08X} start_and_wait...".format(get_ident()))
        # rmv self.start()  # fix: Start the thread here
        self._open_for_business = Event()
        with self._lock:
            assert self._thread is None
            self._thread = Thread(target=self.run, name=type(self).__name__)
            self._thread.start()
        logger.info("{:08X} Thread started.  Waiting for it to be open for business.".format(get_ident()))
        self._open_for_business.wait()
        self._open_for_business = None
        logger.info("{:08X} start_and_wait.".format(get_ident()))

    def join(self):
        logger.info("{:08X} join...".format(get_ident()))
        with self._lock:
            our_thread = self._thread
        if our_thread:
            our_thread.join()
        logger.info("{:08X} join.".format(get_ident()))

    def open_for_business(self):
        # logger.info('{} open for business'.format(self.name).format(get_ident()))
        self._open_for_business.set()

    def _stop_now(self):
        self._keep_running = False

    def startup(self):
        logger.info("{:08X} startup...".format(get_ident()))
        self._keep_running = True # self._ok_to_start
        self._start_before = None
        self.open_for_business()  # Push down to children.
        logger.info("{:08X} startup.".format(get_ident()))

    def process_one(self):
        logger.info("{:08X} process_one...".format(get_ident()))
        sleep(5.0)
        self._stop_now()
        logger.info("{:08X} process_one.".format(get_ident()))
        return True

    def loop(self):
        while self._keep_running:
            self.process_one()
        return False

    def run(self):
        logger.info("{:08X} run...".format(get_ident()))
        try:
            self.startup()
            try:
                while self._keep_running:
                    if not self.loop():
                        self._keep_running = False
            finally:
                self.shutdown()
        except Exception as e:
            # fix? Call a method on self about the exception?
            logging.error("Exception: %s" % str(e), exc_info=1)
            os._exit(42) # Make sure entire application exits

    def shutdown(self):
        with self._lock:
            self._thread = None  # rmv? keep? protect?

