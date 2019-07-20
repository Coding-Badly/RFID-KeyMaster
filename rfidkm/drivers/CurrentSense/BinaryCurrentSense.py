import time
import logging
import os
from rfidkm.drivers.CurrentSense.CurrentSense import CurrentSense

class BinaryCurrentSense(CurrentSense):
	def setup(self):
		self.interface = self.getDriver('currentsense_interface')
		self.threshold = int(self.config['threshold'])
		self.startup = True
		return True

	def getValue(self):
		return self.interface.input(self.config['interface_position']) >= self.threshold

	def	loop(self):
		if self.startup:
			self.current_value = self.getValue()

		time.sleep(0.1)
		new_value = self.getValue()
		if self.current_value != new_value:
			self.current_value = new_value
			self.emit('current_change', new_value)

