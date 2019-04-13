"""=============================================================================

  DriverWontStartError for RFID-KeyMaster.  DriverWontStartError is raised in 
  DriverGroup.start if one or more drivers has indicated that they are not 
  ok_to_start.
  
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

def english_list(sequence, singular, plural):
    l1 = len(sequence)
    if l1 == 0:
        return ''
    elif l1 == 1:
        return (sequence[0], singular)
    elif l1 == 2:
        return (' and '.join(sequence), plural)
    else:
        return (', and '.join((', '.join(sequence[0:-1]), sequence[-1:][0])), plural)

def driver_class_and_name(driver):
    n1 = type(driver).__name__
    n2 = driver.name
    if n1 != n2:
        return n1 + ' / ' + n2
    else:
        return n1

class DriverWontStartError(Exception):
    def __init__(self, not_ok_to_start):
        self.not_ok_to_start = not_ok_to_start
        for_the_human = [driver_class_and_name(driver) for driver in not_ok_to_start]
        self.message = 'A failure with the {} {} prevents the application from starting.'.format(*english_list(for_the_human, 'driver', 'drivers'))

