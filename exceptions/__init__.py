"""=============================================================================

  All exceptions for RFID-KeyMaster.  This package contains all exceptions that
  RFID-KeyMaster could raise

  ----------------------------------------------------------------------------

  Copyright 2019 Mike Cole (aka @Draco, MikeColeGuru)
  Copyright 2019 Brian Cook (aka @Brian, Coding-Badly)

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

============================================================================="""

class DriverClassNameConflict(Exception):
    """One or more drivers have the same class name.

    DriverClassNameConflict is raised in LoadableDriverLoader.__init__ if the
    number of driver modules found is not the same as the number of driver
    classes added to the dictionary.  The difference indicates a driver class
    name conflict.
    """

class DriverClassNotFoundError(Exception):
    """Driver Class not found trying to load a driver.

    :class_name: class name of the driver.

    DriverClassNotFoundError is raised in LoadableDriverLoader if class_name
    cannot be found in the dictionary of driver classes.
    """
    def __init__(self, class_name):
        super().__init__('The driver class {} cannot be found.'.format(class_name))

def english_list(sequence, singular, plural):
    """Return a list in proper English format.

    Args:
        sequence: list of items
        singular: word to return if sequence length is one
        plural: word to return if sequence length is more than one
    Returns:
        A text string with all elements of sequence formatted as in proper
        English.  If sequence is empty and empty string is returned.  Either
        singular or plural is returned depending on the length of sequence.
    """
    le1 = len(sequence)
    if le1 == 0:
        return ''
    if le1 == 1:
        return (sequence[0], singular)
    if le1 == 2:
        return (' and '.join(sequence), plural)
    return (', and '.join((', '.join(sequence[0:-1]), sequence[-1:][0])), plural)

def driver_class_and_name(driver):
    """Return a driver's class and name or just the name if the two are the same.
    """
    # pylint: disable=no-else-return
    na1 = type(driver).__name__
    na2 = driver.name
    if na1 != na2:
        return na1 + ' / ' + na2
    else:
        return na1

class DriverWontStartError(Exception):
    """Driver indicated it won't start.

    :not_ok_to_start: list of drivers (descendents of DriverBase) that
      indicated they won't start

    DriverWontStartError is raised in DriverGroup.start if any drivers have
    indicated that they are not ok_to_start.
    """
    def __init__(self, not_ok_to_start):
        self.not_ok_to_start = not_ok_to_start
        for_the_human = [driver_class_and_name(driver) for driver in not_ok_to_start]
        super().__init__('A failure with the {} {} prevents the application from starting.' \
                .format(*english_list(for_the_human, 'driver', 'drivers')))

class WritableMismatchError(Exception):
    """TwoPhaser failed to correctly determine is-writable.
    """
    def __init__(self):
        super().__init__('Guessed writable does not match actual writable.')

class LeftOverEdgesError(Exception):
    """Cycle detected trying to determine the driver start order.

    LeftOverEdgesError is raised in DriverBase._check_in_start_order if a cycle
    is detected.  This is typically caused by failing to set
    determines_start_order to False when a call to subscribe should not
    determine the driver start order.
    """
    def __init__(self):
        super().__init__('Cycle detected trying to determine the driver start order.' \
                + '  Did you forgot to set determines_start_order to False?')
