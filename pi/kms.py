#!/usr/bin/env python3
"""=============================================================================

  kms for RFID-KeyMaster.  kms (KeyMaster Setup) prepares a Raspberry Pi for
  RFID-KeyMaster development.  This module does the actual work.  kms (no 
  extension) is a bash script that creates a service that runs this code.
  Running the following puts the whole mess in motion...

  ----------------------------------------------------------------------------

  Copyright 2019 Brian Cook (aka Coding-Badly)

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
import pathlib
import requests
import subprocess
import time

class CurrentStepManager():
    def __init__(self):
        self._path_step = pathlib.Path('kms.step')
        self._current_step = None
    def get_current_step(self):
        if self._current_step is None:
            try:
                current_step_text = self._path_step.read_text()
                self._current_step = int(current_step_text)
            except FileNotFoundError:
                self._current_step = 1
        return self._current_step
    def increment_current_step(self):
        _ = self.get_current_step()
        self._current_step += 1
        self._path_step.write_text(str(self._current_step))

def wall(text):
    subprocess.run(['wall',text], check=True)

def wall_and_print(text):
    wall(text)
    print(text)

def update_then_upgrade():
    time.sleep(10.0)
    wall('Update the APT package list.')
    subprocess.run(['apt-get','-y','update'], check=True)
    wall('Upgrade APT packages.')
    subprocess.run(['apt-get','-y','upgrade'], check=True)

def simple_get(source_url, destination_path):
    r = requests.get(source_url, stream=True)
    r.raise_for_status()
    with destination_path.open('wb') as f:
        for chunk in r.iter_content(64*1024):
            f.write(chunk)

need_reboot = False

csm = CurrentStepManager()

go_again = True

while go_again:
    go_again = False
    if csm.get_current_step() == 1:
        wall_and_print('Step #1: Ensure the operating system is up-to-date.')
        update_then_upgrade()
        need_reboot = True
        csm.increment_current_step()
    elif csm.get_current_step() == 2:
        wall_and_print('Step #2: Ensure the operating system is up-to-date again.')
        update_then_upgrade()
        need_reboot = True
        csm.increment_current_step()
    elif csm.get_current_step() == 3:
        wall_and_print('Step #3: Install pip.')
        path_get_pip = pathlib.Path('get-pip.py')
        simple_get('https://bootstrap.pypa.io/get-pip.py', path_get_pip)
        subprocess.run(['python3',str(path_get_pip)], check=True)
        path_get_pip.unlink()
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 4:
        wall_and_print('Step #4: Install Python support for generating a new password.')
        subprocess.run(['pip','install', 'xkcdpass'], check=True)
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 5:
        wall_and_print('Step #5: Set the password using the https://xkcd.com/936/ technique.')
        from xkcdpass import xkcd_password as xp
        wordfile = xp.locate_wordfile()
        mywords = xp.generate_wordlist(wordfile=wordfile, min_length=5, max_length=8)
        new_password = xp.generate_xkcdpassword(mywords, delimiter=',', numwords=3)
        wall_and_print('  The new password is...')
        wall_and_print('  {}'.format(new_password))
        # fix: Send the new password to a repository.
        new_password = 'whatever'  # rmv
        pi_new_password = ('pi:' + new_password).encode('ascii')
        subprocess.run("chpasswd", input=pi_new_password, check=True)
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 6:
        wall_and_print('Step #6: Change the hostname.')
        path_hostname = pathlib.Path('/etc/hostname')
        path_hostname.write_text('RFID-KeyMaster-T01\n')
        subprocess.run(['sed','-i',"s/raspberrypi/RFID-KeyMaster-T01/",'/etc/hosts'], check=True)
        need_reboot = True
        csm.increment_current_step()
    elif csm.get_current_step() == 7:
        wall_and_print('Step #7: Change the timezone.')
        # Why localtime has to be removed...
        # https://bugs.launchpad.net/ubuntu/+source/tzdata/+bug/1554806
        pathlib.Path('/etc/timezone').write_text('America/Chicago\n')
        pathlib.Path('/etc/localtime').unlink()
        subprocess.run(['dpkg-reconfigure','-f','noninteractive','tzdata'], check=True)
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 8:
        wall_and_print('Step #8: Change the keyboard layout.')
        # debconf-get-selections | grep keyboard-configuration
        # The top entry is suspect.  "gb" was the value after changing 
        # keyboards using dpkg-reconfigure.
        keyboard_conf = """
keyboard-configuration\tkeyboard-configuration/xkb-keymap\tselect\tus
keyboard-configuration\tkeyboard-configuration/layoutcode\tstring\tus
keyboard-configuration\tkeyboard-configuration/layout\tselect\tEnglish (US)
keyboard-configuration\tkeyboard-configuration/variant\tselect\tEnglish (US)
""".encode("ascii")
        subprocess.run("debconf-set-selections", input=keyboard_conf, check=True)
        subprocess.run(['dpkg-reconfigure','-f','noninteractive','keyboard-configuration'], check=True)
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 9:
        wall_and_print('Step #9: Change the locale.')
        locale_conf = """
locales\tlocales/locales_to_be_generated\tmultiselect\ten_US.UTF-8 UTF-8
locales\tlocales/default_environment_locale\tselect\ten_US.UTF-8
""".encode("ascii")
        subprocess.run("debconf-set-selections", input=locale_conf, check=True)
        subprocess.run(['sed','-i',"s/^# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/",'/etc/locale.gen'], check=True)
        subprocess.run(['dpkg-reconfigure','-f','noninteractive','locales'], check=True)
        subprocess.run(['update-locale','LANG=en_US.UTF-8'], check=True)
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 10:
        wall_and_print('Step #10: Install Git.')
        subprocess.run(['apt-get','-y','install','git'], check=True)
        go_again = True
        csm.increment_current_step()
    # fix? Configure Git for Github?
    # fix: Clone RFID-KeyMaster
    elif csm.get_current_step() == 11:
        wall_and_print('Step #11: One last reboot for good measure.')
        need_reboot = True
        csm.increment_current_step()
    # fix: Configure RFID-KeyMaster to automatically run on boot.
    else:
        wall_and_print('RFID-KeyMaster installed.  Disabling the kms service.')
        subprocess.run(['systemctl','disable','kms.service'], check=True)

if need_reboot:
    wall_and_print('REBOOT!')
    time.sleep(10.0)
    subprocess.run(['reboot'], check=True)

