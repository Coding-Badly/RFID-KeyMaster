

class RequiredEventException(Exception):
    def __init__(self, event_name):
        super().__init__('Could not find the required event "' + str(event_name) + '".')
