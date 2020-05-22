
import time
from enum import Enum
from typing import Union, List, Optional

import asyncio
from pymata_aio.pymata3 import PyMata3
from pymata_aio.private_constants import PrivateConstants
from pymata_aio.constants import Constants

from klgists.common.silenced import silenced
from klgists.common.exceptions import ExternalDeviceNotFound, NoSuchOutputPinException, BadPinWriteValueException

from sauronlib import logger
from .board_layout import BoardLayout
from .stimulus import StimulusType


class StatusCode(Enum):
	def __new__(cls, *args, **kwds):
		value = len(cls.__members__) + 1
		obj = object.__new__(cls)
		obj._value_ = value
		return obj

	def __init__(self, pattern: List[int]):
		self.pattern = pattern

	INIT = [400, 100] * 2
	SHUTDOWN = [100, 400] * 2
	SUCCESS = [300] * 3
	WARNING = [50, 175] * 5
	ERROR = [25, 100] * 8
	READY = [300] * 3


class Board:
	"""An abstract Arduino board. You must use a concrete subclass.
	Supports stimuli (output), sensors (input), and digital 'startup pins' that are set on start.
	You should use a Board with a with statement:
		with MyBoardClass() as board:
			...
	"""
	def __init__(self, layout: BoardLayout, reset_time: Optional[int] = 100, sampling_interval_ms: int = 100, connection_port: Optional[str] = None) -> None:
		self.layout = layout
		self._reset_time = reset_time
		self._sampling_interval_ms = sampling_interval_ms
		self._connection_port = connection_port

	def _new_board(self):
		"""Override this to return a PyMata3-like object.
		It must implement most functions in PyMata3.
		"""
		raise NotImplementedError()

	def __enter__(self):
		self.init()
		return self

	def __repr__(self) -> str:
		return "Board(port{}: {}; sampling@{}ms)".format(self._connection_port, self.layout, self._sampling_interval_ms)
	def __str__(self): return repr(self)

	def __exit__(self, type, value, traceback) -> None:
		self.exit()

	def reset(self):
		self._board.send_reset()
		logger.debug("Sent reset to Arduino board")

	def register_sensor(self, pin: int, callback) -> None:
		if isinstance(pin, int):
			pin_number = pin
		elif pin in self.layout.digital_sensors[pin]:
			pin_number = self.layout.digital_sensors[pin]
		elif pin in self.layout.analog_sensors:
			pin_number = self.layout.digital_sensors
		else:
			raise KeyError("No sensor pin for sensor {}".format(pin))
		pin_state = self._board.get_pin_state(pin_number)
		logger.debug("Registered sensor on pin {}".format(pin_number))
		self._board.enable_analog_reporting(pin=pin_number)
		# TODO should be able to use pin_state[1] instead of Constants.ANALOG, but for some reason the setting doesn't stick??
		self._board.set_pin_mode(pin_number=pin_number, pin_state=Constants.ANALOG, callback=callback, cb_type=Constants.CB_TYPE_DIRECT)

	def reset_sensor(self, pin_number: int) -> None:
		self._board.disable_analog_reporting(pin=pin_number)

	def exit(self) -> None:
		logger.info("Setting pins to off and shutting down Arduino")
		try:
			self.stop_all_stimuli()
			self.set_illumination(0)
			self.reset_all_sensors()
			self.flash_status(StatusCode.SHUTDOWN)
		finally:
			try:
				asyncio.ensure_future(self._kill())
			finally:
				self._board.core.serial_port.my_serial.close()
		logger.debug("Finished shutting down Arudino")

	async def _kill(self):
		try:
			self._board.core.send_reset()
			self._board.core.loop.stop()
			self._board.core.loop.close()
		except:
			logger.exception("Failed to shut down properly")

	def stop_all_stimuli(self) -> None:
		for pin in self.layout.digital_stimuli.values():
			self._board.digital_write(pin, 0)
		for pin in self.layout.analog_stimuli.values():
			self._board.analog_write(pin, 0)

	def reset_all_sensors(self):
		for pin in self.layout.digital_sensors.values():
			self._board.disable_digital_reporting(pin)
		for pin in self.layout.analog_sensors.values():
			self._board.disable_analog_reporting(pin)

	def flash_status(self, status: StatusCode):
		pin = self.layout.status_led_pin
		for i, delta in enumerate(status.pattern):
			self._board.digital_write(pin, i % 2)
			self._board.sleep(status.on_ms/1000)
		self._board.digital_write(pin, 1)

	def sleep(self, seconds: float) -> None:
		self._board.sleep(seconds)
	def sleep_ms(self, seconds: float) -> None:
		self._board.sleep(seconds / 1000)

	def set_stimulus_max(self, stim_name: str) -> None:
		if self.is_digital(stim_name):
			self.set_stimulus(stim_name, 1)
		else:
			self.set_stimulus(stim_name, 255)

	def set_illumination(self, value: Union[int, bool]):
		for pin in self.layout.startup_pins:
			self._board.digital_write(pin, int(value))

	def set_stimulus(self, stim_name: str, value: int) -> None:
		"""Sets an analog or digital stimulus. For external calls."""
		if self.is_digital(stim_name):
			if value != 0 and value != 1:
				raise BadPinWriteValueException("Value {} is out of range for digital stimulus {}".format(value, stim_name))
			self._board.digital_write(self.layout.digital_stimuli[stim_name], value)
		elif self.is_analog(stim_name):
			if value > 255 or value < 0:
				raise BadPinWriteValueException("Value {} is out of range for analog stimulus {}".format(value, stim_name))
			self._board.analog_write(self.layout.analog_stimuli[stim_name], value)

	def set_analog_stimulus(self, stim_name: str, value: int) -> None:
		"""For external calls; performs a value check."""
		if value > 255 or value < 0: raise BadPinWriteValueException("Analog write value must be between 0 and 255; was {}".format(value))
		self._board.analog_write(self.layout.analog_stimuli[stim_name], value)

	def set_digital_stimulus(self, stim_name: str, value: int) -> None:
		"""For external calls; performs a value check."""
		if value not in (0, 1): raise BadPinWriteValueException("Digital write value must be 0 or 1; was {}".format(value))
		self._board.digital_pin_write(self.layout.digital_stimuli[stim_name], value)

	def is_digital(self, stimulus_name: str) -> bool:
		return self.stimulus_type(stimulus_name) is StimulusType.DIGITAL
	def is_analog(self, stimulus_name: str) -> bool:
		return self.stimulus_type(stimulus_name) is StimulusType.ANALOG

	def stimulus_type(self, stimulus_name: str) -> StimulusType:
		"""Returns either 'digital' or 'analog'."""
		if stimulus_name in self.layout.analog_stimuli:
			return StimulusType.ANALOG
		elif stimulus_name in self.layout.digital_stimuli:
			return StimulusType.DIGITAL
		else:
			raise NoSuchOutputPinException("No stimulus with name {} exists".format(stimulus_name))

	# TODO read_sensor method

	def read_digital_sensor(self, sensor_name: str):
		self._board.digital_read(self.layout.digital_sensors[sensor_name])

	def read_analog_sensor(self, sensor_name: str):
		self._board.analog_read(self.layout.analog_sensors[sensor_name])

	def init(self) -> None:
		# config['sauron.hardware.arduino.reset_time']
		# config.sensors['sampling_interval_milliseconds']
		self._connect()
		self.flash_status(StatusCode.INIT)
		self._init_pins()
		self.set_illumination(1)
		logger.info('Finished initializing board')

	def write_digital_pins_by_ports(self, names: List[str], value: int) -> None:
		"""Writes digital pins port-by-port."""
		if value not in [0, 1]: raise ValueError("Must be a digital value (0 or 1)")
		pins = [self.layout.digital_stimuli[name] for name in names]  # TODO we want pins, right?
		pins_to_ports = {stimulus: port for port, stimulus in self.layout.digital_ports.items() if stimulus in pins}
		if len(pins_to_ports) != len(names): raise ValueError("Cannot write: not all of the stimuli are digital output pins")
		for port in pins_to_ports.values():
			self._set_port(port, value == 1)

	def _connect(self) -> None:
		def board_load_error():
			raise ExternalDeviceNotFound('Could not connect to the Arduino board') from None  # from None means ignore the first error
		try:
			with silenced(no_stdout=True, no_stderr=False):
				self._board = self._new_board()
		except (TypeError, ValueError) as e:
			board_load_error()
		if self._board is None: board_load_error()
		self._board.set_sampling_interval(self._sampling_interval_ms)

	def _init_pins(self) -> None:
		# If you check the code in set_pin_mode, you'll find that the pin state is ignored for input pins
		# Instead, it's set only if a callback is passed
		# This means we can't set the type to Constants.INPUT here
		for name, pin in self.layout.analog_stimuli.items():
			self._board.set_pin_mode(pin, Constants.PWM)
		for name, pin in self.layout.analog_sensors.items():
			self._board.set_pin_mode(pin, Constants.ANALOG)

	def _set_port(self, port: int, on: bool) -> None:
		# TODO is this correct?
		raise NotImplementedError()
		#port = pin // 8
		calculated_command = PrivateConstants.DIGITAL_MESSAGE + port
		#mask = 1 << (pin % 8)
		mask = 1 << port
		# Calculate the value for the pin's position in the port mask
		if on:
			PrivateConstants.DIGITAL_OUTPUT_PORT_PINS[port] |= mask
		else:
			PrivateConstants.DIGITAL_OUTPUT_PORT_PINS[port] &= ~mask
		# Assemble the command
		command = (
			calculated_command,
			PrivateConstants.DIGITAL_OUTPUT_PORT_PINS[port] & 0x7f,
			(PrivateConstants.DIGITAL_OUTPUT_PORT_PINS[port] >> 7) & 0x7f
		)
		#await self._board._send_command(command)


class ExtendedBoard(Board):
	"""An abstract board with extra functionality."""

	def strobe(self, stim_name: str, duration: float=10, isi_seconds: float=0.5, pwm_value: int=255) -> None:
		"""Strobes an analog or digital stimulus at an inter-stimulus interval for a duration."""
		if self.is_digital(stim_name):
			pwm_value = 1
		t0 = time.monotonic()
		while time.monotonic() - t0 < duration:
			self.set_stimulus(stim_name, pwm_value)
			self._board.sleep(isi_seconds)
			self.set_stimulus(stim_name, 0)
			self._board.sleep(isi_seconds)

	def bump(self, stim_name: str, power_up: float=255, power_down: float = 70, up_ms: float=20, down_ms: float=1000) -> None:
		if self.is_digital(stim_name): power_up = power_down = 1
		t0 = time.monotonic()
		self.set_stimulus(stim_name, int(power_up))
		self._board.sleep(up_ms/1000.0)
		self.set_stimulus(stim_name, int(power_down))
		self._board.sleep(down_ms/1000.0)
		self.set_stimulus(stim_name, 0)

	def pulse(self, stim_name: str, sleep_seconds: float = 1, pwm_value: int = 255) -> None:
		"""Turns a pin on, then off."""
		if self.is_digital(stim_name): pwm_value = 1
		self.set_stimulus(stim_name, pwm_value)
		self._board.sleep(sleep_seconds)
		self.set_stimulus(stim_name, 0)


class PymataBoard(ExtendedBoard):
	"""The main concrete Board implementation.
	Simply starts a PyMata3 board as expected.
	"""
	def _new_board(self) -> PyMata3:
		return PyMata3(self._reset_time, com_port=self._connection_port, log_output=True, serial_timeout=0, serial_write_timeout=1)


__all__ = ['Board', 'ExtendedBoard', 'PymataBoard', 'StatusCode']
