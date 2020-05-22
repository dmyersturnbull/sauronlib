import datetime
from os.path import dirname
from typing import Callable, List

import pandas as pd
from hipsterplot import HipsterPlotter

from klgists.files import make_dirs

from sauronlib import logger
from sauronlib.sensors.sensor import *


class ArduinoCsvSensor(PlottableSensor):
	"""An abstract sensor that uses Arduino sensor callbacks and writes Value,Time column to a CSV file.
	Example usage:
	MyImplementation('data.csv', lambda r: board.register_sensor(pin, r), board.reset_sensor)
	"""
	def __init__(self, output_path: str, activation_callback: Callable[[Callable[[List[float]], None]], None], deactivation_callback: Callable[[], None]) -> None:
		"""
		:param output_path: A CSV file to record to. Will contain columns 'Value' and 'Time'.
		:param activation_callback: Ex: lambda inner_callback: board.register_sensor(pin, inner_callback)
		:param deactivation_callback: Ex: lambda: board.reset_sensor(pin)
		"""
		super(ArduinoCsvSensor, self).__init__()
		self.output_path = output_path
		self.activation_callback = activation_callback
		self.deactivation_callback = deactivation_callback

	def _arm(self) -> None:
		logger.info("Recording {} to {}".format(self.name(), self.output_path))
		make_dirs(dirname(self.output_path))
		self.log_file = open(self.output_path, 'a')
		self.log_file.write('Value,Time\n')
		self.activation_callback(self._record)

	def _record(self, data: List[float]) -> None:
		self.log_file.write('%s,%s\n' % (data[1], datetime.datetime.now()))
		self.previous_value = data[1]

	def _disarm(self) -> None:
		self.deactivation_callback()
		self.log_file.close()

	def _fire(self) -> None: pass

	def plot(self):
		fmt = '%Y-%m-%d %H:%M:%S.%f'
		df = pd.read_csv(self.output_path)
		if len(df) == 0:
			return '{}: <no data>'.format(self.sensor_name())
		low_x = datetime.datetime.strptime(df['Time'].iloc[0], fmt).strftime('%H:%M:%S')
		high_x = datetime.datetime.strptime(df['Time'].iloc[-1], fmt).strftime('%H:%M:%S')
		s = HipsterPlotter(num_y_chars=10).plot(df['Value'], title=self.name(), low_x_label=low_x, high_x_label=high_x)
		with open(self.output_path + '.plot.txt', 'w', encoding="utf8") as f:
			f.write(s)
		return s


class Thermometer(ArduinoCsvSensor):
	pass

class Photometer(ArduinoCsvSensor):
	pass


__all__ = ['ArduinoCsvSensor', 'Thermometer', 'Photometer']
