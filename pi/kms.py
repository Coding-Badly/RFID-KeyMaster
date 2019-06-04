#!/usr/bin/env python3
"""=============================================================================

  kms for RFID-KeyMaster.  kms (KeyMaster Setup) prepares a Raspberry Pi for
  RFID-KeyMaster development.  This module does the actual work.  kms (no 
  extension) is a bash script that creates a service that runs this code.
  Running the following puts the whole mess in motion...

curl -s "https://raw.githubusercontent.com/Coding-Badly/RFID-KeyMaster/006/develop/brian/pi/kms" | bash

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
import grp
import json
import os
import pathlib
import pwd
import requests
import subprocess
import time
import uuid

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

class DirectoryMaker():
    def __init__(self, default_final_mode=0o700):
        self._default_final_mode = default_final_mode
        self._uid = pwd.getpwnam("pi").pw_uid
        self._gid = grp.getgrnam("pi").gr_gid
    def mkdir(self, path, parents=False, final_mode=None):
        final_mode = self._default_final_mode if final_mode is None else final_mode
        path.mkdir(mode=0o777, parents=parents, exist_ok=True)
        os.chown(str(path), self._uid, self._gid)
        path.chmod(final_mode)
    def chown(self, path):
        os.chown(str(path), self._uid, self._gid)

def wall(text):
    subprocess.run(['wall',text], check=True)

def wall_and_print(text, step=None):
    if step is not None:
        text = 'Step #{}: {}'.format(int(step), text)
    wall(text)
    print(text)

def update_then_upgrade():
    time.sleep(5.0)
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

def check_global_config():
    global global_config
    if path_kms_json.exists():
        with path_kms_json.open() as f:
            global_config = json.load(f)
    else:
        global_config = dict()

csm = CurrentStepManager()

path_kms_json = pathlib.Path('kms.json')
check_global_config()

need_reboot = False

go_again = True
while go_again:
    go_again = False
    if csm.get_current_step() == 1:
        wall_and_print('Ensure the operating system is up-to-date.', csm.get_current_step())
        update_then_upgrade()
        need_reboot = True
        csm.increment_current_step()
    elif csm.get_current_step() == 2:
        wall_and_print('Install Git.', csm.get_current_step())
        subprocess.run(['apt-get','-y','install','git'], check=True)
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 3:
        wall_and_print('Install Python development.', csm.get_current_step())
        subprocess.run(['apt-get','-y','install','python3-dev'], check=True)
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 4:
        wall_and_print('Ensure the operating system is up-to-date again.', csm.get_current_step())
        update_then_upgrade()
        need_reboot = True
        csm.increment_current_step()
    elif csm.get_current_step() == 5:
        wall_and_print('Install pip.', csm.get_current_step())
        path_get_pip = pathlib.Path('get-pip.py')
        simple_get('https://bootstrap.pypa.io/get-pip.py', path_get_pip)
        subprocess.run(['python3',str(path_get_pip)], check=True)
        path_get_pip.unlink()
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 6:
        wall_and_print('Install Python modules required by this module.', csm.get_current_step())
        subprocess.run(['pip','install', 'xkcdpass'], check=True)
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 7:
        wall_and_print('Get the global configuration file.', csm.get_current_step())
        base_url = os.environ.get('KMS_BASE_URL', 'https://raw.githubusercontent.com/Coding-Badly/RFID-KeyMaster/006/develop/brian/pi')
        get_this = base_url + '/' + 'kms.json'
        try:
            simple_get(get_this, path_kms_json)
        except requests.exceptions.HTTPError:
            pass
        check_global_config()
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 8:
        wall_and_print('Set the password using the https://xkcd.com/936/ technique.', csm.get_current_step())
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
    elif csm.get_current_step() == 9:
        wall_and_print('Change the hostname.', csm.get_current_step())
        path_hostname = pathlib.Path('/etc/hostname')
        path_hostname.write_text('RFID-KeyMaster-T01\n')
        subprocess.run(['sed','-i',"s/raspberrypi/RFID-KeyMaster-T01/",'/etc/hosts'], check=True)
        need_reboot = True
        csm.increment_current_step()
    elif csm.get_current_step() == 10:
        wall_and_print('Change the timezone.', csm.get_current_step())
        # Why localtime has to be removed...
        # https://bugs.launchpad.net/ubuntu/+source/tzdata/+bug/1554806
        # date "+%Z %z"
        pathlib.Path('/etc/timezone').write_text('America/Chicago\n')
        pathlib.Path('/etc/localtime').unlink()
        subprocess.run(['dpkg-reconfigure','-f','noninteractive','tzdata'], check=True)
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 11:
        wall_and_print('Change the keyboard layout.', csm.get_current_step())
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
    elif csm.get_current_step() == 12:
        wall_and_print('Change the locale.', csm.get_current_step())
        # locale
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
    elif csm.get_current_step() == 13:
        wall_and_print('Configure Git.', csm.get_current_step())
        this_mac = format(uuid.getnode(), 'X')
        config_by_this_mac = global_config.get(this_mac, None)
        config_github = config_by_this_mac.get('github', None) if config_by_this_mac else None
        if config_github:
            # Set basic Git configuration.
            git_user_name = config_github.get('user.name', 'Git User Name Goes Here')
            git_user_email = config_github.get('user.email', 'whomever@dallasmakerspace.org')
            git_core_editor = config_github.get('core.editor', 'nano')
            subprocess.run(['git','config','--system','user.name',git_user_name], check=True)
            subprocess.run(['git','config','--system','user.email',git_user_email], check=True)
            subprocess.run(['git','config','--system','core.editor',git_core_editor], check=True)
            # Ensure the .ssh directory exists.
            path_dot_ssh = pathlib.Path('/home/pi/.ssh')
            # https://superuser.com/questions/215504/permissions-on-private-key-in-ssh-folder
            dm = DirectoryMaker()
            dm.mkdir(path_dot_ssh)
            # Add a Github section to the .ssh/config file.
            path_ssh_config = path_dot_ssh / 'config'
            with path_ssh_config.open('at') as f:
                f.write('Host github.com\n')
                f.write('        User git\n')
                f.write('        Hostname github.com\n')
                f.write('        PreferredAuthentications publickey\n')
                f.write('        IdentityFile ~/.ssh/github/id_rsa\n')
            dm.chown(path_ssh_config)
            # Create a github subdirectory for the Github key pair.
            path_github = path_dot_ssh / 'github'
            dm.mkdir(path_github)
            # Generate the Github key pair.
            path_id_rsa = path_github / 'id_rsa'
            # ssh-keygen -t rsa -C "arduino.tiny@gmail.com" -b 1024 -N '' -f ~/.ssh/github/id_rsa
            subprocess.run(['ssh-keygen','-t','rsa','-C',git_user_email,'-b','4096','-N','','-f',str(path_id_rsa)], check=True)
            dm.chown(path_id_rsa)
            dm.chown(path_id_rsa.with_suffix('.pub'))
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 14:
        wall_and_print('Clone the KeyMaster.', csm.get_current_step())
        # git clone git@github.com:Coding-Badly/RFID-KeyMaster.git /home/pi/RFID-KeyMaster
        # git clone https://github.com/Coding-Badly/RFID-KeyMaster.git /home/pi/RFID-KeyMaster
        subprocess.run(['git','clone','https://github.com/Coding-Badly/RFID-KeyMaster.git','/home/pi/RFID-KeyMaster'], check=True)
        subprocess.run(['git','checkout','-t','remotes/origin/006/develop/brian'], cwd='/home/pi/RFID-KeyMaster', check=True)
        # Change the remote url to use ssh.
        # git remote set-url origin git@github.com:Coding-Badly/RFID-KeyMaster.git
        subprocess.run(['git','remote','set-url','origin','git@github.com:Coding-Badly/RFID-KeyMaster.git'], cwd='/home/pi/RFID-KeyMaster', check=True)
        # Use pip to install dependencies.
        path_requirements = pathlib.Path('/home/pi/RFID-KeyMaster/requirements.txt')
        if path_requirements.exists():
            subprocess.run(['pip','install','-U','-r',str(path_requirements)], check=True)
        # Fix ownership of the RFID-KeyMaster repository.
        subprocess.run(['chown','-R','pi:pi','/home/pi/RFID-KeyMaster'], check=True)
        # Prepare the cache directory.
        dm = DirectoryMaker(default_final_mode=0o755)
        path_cache = pathlib.Path('/var/cache/Dallas Makerspace/RFID-KeyMaster')
        dm.mkdir(path_cache, parents=True)
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 15:
        wall_and_print('Install PiFace Digital 2 packages from GitHub.', csm.get_current_step())
        # Common
        subprocess.run(['git','clone','git://github.com/piface/pifacecommon.git','/home/pi/pifacecommon'], check=True)
        subprocess.run(['python3','/home/pi/pifacecommon/setup.py','install'], cwd='/home/pi/pifacecommon/', check=True)
        subprocess.run(['rm','-rf','/home/pi/pifacecommon'], check=True)
        # Digital I/O
        subprocess.run(['git','clone','git://github.com/piface/pifacedigitalio.git','/home/pi/pifacedigitalio'], check=True)
        subprocess.run(['python3','/home/pi/pifacedigitalio/setup.py','install'], cwd='/home/pi/pifacedigitalio/', check=True)
        subprocess.run(['rm','-rf','/home/pi/pifacedigitalio'], check=True)
        go_again = True
        csm.increment_current_step()
    elif csm.get_current_step() == 16:
        wall_and_print('Install PiFace Digital 2 initialization service.', csm.get_current_step())
        subprocess.run(['cp','/home/pi/RFID-KeyMaster/pi/init_PiFace_Digital_2.service','/etc/systemd/system/init_PiFace_Digital_2.service'], check=True)
        subprocess.run(['systemctl','enable','init_PiFace_Digital_2.service'], check=True)
        #go_again = True
        need_reboot = True
        csm.increment_current_step()
    #elif csm.get_current_step() == 17:
    #    wall_and_print('One last reboot for good measure.', csm.get_current_step())
    #    need_reboot = True
    #    csm.increment_current_step()
    # fix: Configure RFID-KeyMaster to automatically run on boot.
    else:
        wall_and_print('RFID-KeyMaster installed.  Disabling the kms service.')
        subprocess.run(['systemctl','disable','kms.service'], check=True)

if need_reboot:
    wall_and_print('REBOOT!')
    time.sleep(5.0)
    subprocess.run(['reboot'], check=True)

