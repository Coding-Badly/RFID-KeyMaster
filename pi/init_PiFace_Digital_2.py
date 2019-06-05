#!/usr/bin/env python3
"""=============================================================================

  init_PiFace_Digital_2 for RFID-KeyMaster.  init_PiFace_Digital_2 initializes
  all connected PiFace Digital 2 boards.  The boards only need to be
  initialized once after power-up.  This code is meant to run from a service
  during boot.
  
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
try:
  import pifacedigitalio
except ImportError:
  exit()

try:
  pifacedigitalio.core.init()
except pifacedigitalio.core.NoPiFaceDigitalDetectedError:
  exit()

