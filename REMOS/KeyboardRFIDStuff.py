
selector = selectors.DefaultSelector()

device = evdev.InputDevice('/dev/input/by-id/usb-Sycreader_USB_Reader_08FF20150112-event-kbd')
key1 = selector.register(device, selectors.EVENT_READ)

wake_pipe_read, wake_pipe_write = os.pipe()
key2 = selector.register(wake_pipe_read, selectors.EVENT_READ)
selector.select(1.0)

os.write(wake_pipe_write, chr(0).encode())
selector.select(1.0)
# [(SelectorKey(fileobj=5, fd=5, events=1, data=None), 1)]
# [(SelectorKey(fileobj=5, fd=5, events=1, data=None), 1), (SelectorKey(fileobj=InputDevice('/dev/input/by-id/usb-Sycreader_USB_Reader_08FF20150112-event-kbd'), fd=4, events=1, data=None), 1)]

status = selector.select(1.0)
status[0][0]


os.read(wake_pipe_read, 255)

device.read_one()



from enum import Enum
import evdev
import os
import selectors
import threading

class ParserStatus(Enum):
    UNKNOWN = 0
    PENDING = 1
    RESET = 2
    FINI = 3
    ERROR = 4

class SycreaderParser():
    def __init__(self):
        self._rfid = ''
        self._timestamp = None
        self._reset()
    def _process_digit(self, wrapped):
        # KEY_0 through KEY_9
        kc = wrapped.keycode
        if len(kc) == 5:
            digit = kc[-1]
            if (digit >= '0') and (digit <= '9'):
                self._pending += digit
                return True
            return False
    def _reset(self):
        self._state = self.wait_for_first_event
        self._start = None
        self._stop = None
        self._pending = ''
    def wait_for_first_event(self, wrapped):
        if self._process_digit(wrapped):
            self._state = self.collecting
            self._start = wrapped.event.timestamp()
            self._stop = self._start
            return ParserStatus.PENDING
        else:
            # Unexpected keycode
            self._reset()
            return ParserStatus.ERROR
    def collecting(self, wrapped):
        self._stop = wrapped.event.timestamp()
        elapsed = self._stop - self._start
        if elapsed > 0.250:
            self._reset()
            # fix? Report the trouble?
            return ParserStatus.RESET
        if self._process_digit(wrapped):
            return ParserStatus.PENDING
        elif wrapped.keycode == 'KEY_ENTER':
            self._rfid = self._pending
            self._timestamp = self._stop
            self._reset()
            return ParserStatus.FINI
        else:
            # Unexpected keycode
            self._reset()
            # fix? Report the error?
            return ParserStatus.ERROR
    def process(self, wrapped):
        rv2 = ParserStatus.UNKNOWN
        rv1 = self._state(wrapped)
        if rv1 == ParserStatus.RESET:
            rv2 = self._state(wrapped)
        if rv1.value > rv2.value:
            return rv1
        else:
            return rv2
    @property
    def rfid(self):
        # fix? Report trouble / raise an exception if ParserStatus.FINI was not reached?
        return self._rfid
    @property
    def timestamp(self):
        return self._timestamp

class ProcessSwipe():
    def __init__(self, target):
        self.target = target
        self.parser = SycreaderParser()
    def execute(self, key):
        while True:
            event = key.fileobj.read_one()
            if event is None:
                break
            if event.type == evdev.ecodes.EV_KEY:
                cooked = evdev.util.categorize(event)
                if cooked.keystate == cooked.key_up:
                    rv = self.parser.process(cooked)
                    if rv == ParserStatus.FINI:
                        self.target.got_swipe(self.parser)

class SetRunningFalse():
    def __init__(self, target):
        self.target = target
    def execute(self, key):
        _ = os.read(key.fd, 1)
        self.target.running = False

def find_el_cheapo_rfid_reader():
    return [device for device in [evdev.InputDevice(path) for path in evdev.list_devices()] if 'SYCREADER' in device.name.upper()]

class KeyboardRFID(threading.Thread):
    def __init__(self):
        super().__init__()
        self.selector = selectors.DefaultSelector()
        #self.device = evdev.InputDevice('/dev/input/by-id/usb-Sycreader_USB_Reader_08FF20150112-event-kbd')
        self.device = find_el_cheapo_rfid_reader()[0]
        self.key1 = self.selector.register(self.device, selectors.EVENT_READ, ProcessSwipe(self))
        self.wake_pipe_read, self.wake_pipe_write = os.pipe()
        self.key2 = self.selector.register(self.wake_pipe_read, selectors.EVENT_READ, SetRunningFalse(self))
        self.running = True
    def run(self):
        while self.running:
            status = self.selector.select()
            if len(status) > 0:
                for row in status:
                    key = row[0]
                    # row[1] is an event mask.  We only registered EVENT_READs so it's ignored.
                    key.data.execute(key)
    def got_swipe(self, parser):
        # Fastest possible swipe rate appears to be ~0.5 seconds.
        print(parser.timestamp, parser.rfid)
    def teardown(self):
        self.selector.unregister(self.wake_pipe_read)
        self.key2 = None
        self.selector.unregister(self.device)
        self.key1 = None
        os.close(self.wake_pipe_write)
        self.wake_pipe_write = None
        os.close(self.wake_pipe_read)
        self.wake_pipe_read = None
        self.device.close()
        self.device = None

tm1 = KeyboardRFID()
tm1.start()

#os.write(tm1.wake_pipe_write, chr(0).encode())

#tm1.teardown()

