
from typing import List, Dict

from klgists.common import flatten
from klgists.common.exceptions import BadConfigException


class BoardLayout:
	"""The pins and ports on an Arduino board.
	Defines which correspond to input and output stimuli and sensors.
	Does not know about sensors or stimuli themselves, only about their pins and names.
	"""
	def __init__(
			self,
			digital_ports: Dict[int, List[int]], analog_ports: Dict[int, List[int]], status_led_pin: int,
			digital_stimuli: Dict[str, int]=None, analog_stimuli: Dict[str, int]=None,
			digital_sensors: Dict[str, int]=None, analog_sensors: Dict[str, int]=None,
			startup_pins: List[int]=None,
	):
		self.digital_ports = digital_ports
		self.analog_ports = analog_ports
		self.status_led_pin = status_led_pin
		self.digital_stimuli = {} if digital_stimuli is None else digital_stimuli  # type: Dict[str, int]
		self.analog_stimuli = {} if analog_stimuli is None else analog_stimuli  # type: Dict[str, int]
		self.stimuli = self.digital_stimuli.copy()
		self.stimuli.update(self.analog_stimuli)
		self.digital_sensors = {} if digital_sensors is None else digital_sensors  # type: Dict[str, int]
		self.analog_sensors = {} if analog_sensors is None else analog_sensors  # type: Dict[str, int]
		self.startup_pins = {} if startup_pins is None else startup_pins  # type: List[int]
		# overlap
		output_overlap = set(digital_stimuli).intersection(analog_stimuli)
		input_overlap = set(digital_sensors).intersection(analog_sensors)
		# TODO wrong error type
		if len(output_overlap) != 0:
			raise BadConfigException("There is overlap between digital and analog stimulus pins {}".format(output_overlap))
		if len(input_overlap) != 0:
			raise BadConfigException("There is overlap between digital and analog sensor pins {}".format(input_overlap))
		# allowed pins
		self.allowed_digital_pins = flatten([[pin for pin in allowed] for port, allowed in digital_ports.items()])  # type: List[int]
		self.allowed_analog_pins = flatten([[pin for pin in allowed] for port, allowed in analog_ports.items()])  # type: List[int]

	def __repr__(self) -> str:
		return "BoardLayout(digital_ports={}, analog_ports={}, digital_out={}, analog_out={}, digital_in={}, digital_out={}, startup={})"\
			.format(self.digital_ports, self.analog_ports, self.digital_stimuli, self.analog_stimuli, self.digital_sensors, self.analog_sensors, self.startup_pins)

	def __str__(self): return repr(self)


__all__ = ['BoardLayout']
