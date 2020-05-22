import threading
from typing import Set, Any


class Sensor:
	"""An abstract device to record to a stream, file, or otherwise.
	Can be armed, disarmed, and fired. Every implementation must implement all three (_arm(), _disarm(), and _fire()).
	However, they do not need to _do anything_ in response to these calls.
	Most sensors fall into one of two classes:
		- Arming begins recording and disarming stops it.
		- Arming simply primes, and starts for a specified duration, indefinite period, or single shot.
			Disarming stops recording if applicable and closes.
	Calling fire() causes _fire() to be called in a new thread. If sensor does not support firing, it can exit immediately.
	"""
	def __init__(self):
		self._thread = threading.Thread(target=self._fire)  # type: threading.Thread
		self._is_armed = False  # type: bool
		self.should_kill = [None]

	def _arm(self) -> None:
		raise NotImplementedError()
	def _fire(self) -> None:
		raise NotImplementedError()
	def _disarm(self) -> None:
		raise NotImplementedError()
	def _save(self):
		raise NotImplementedError()

	def arm(self) -> None:
		self.should_kill[0] = False
		self._arm()
		self._is_armed = True

	def disarm(self) -> None:
		self.should_kill[0] = True
		self._disarm()
		self._is_armed = False

	def fire(self) -> None:
		assert self.is_armed()
		self._thread.start()  # calls _fire

	def is_armed(self) -> bool: return self._is_armed

	@classmethod
	def sensor_name(cls) -> str: return cls.__name__.lower()
	def __str__(self): return self.name() + " (" + ('armed' if self.is_armed() else 'disarmed') + ")"
	def name(self) -> str: return self.__class__.__name__.lower()


class PlottableSensor(Sensor):
	def plot(self) -> str:
		raise NotImplementedError()


class TriggeredSensor(Sensor):
	"""
	A sensor that arms, disarms, and fires in response to arbitrary triggers, such as "board_initialized" or "experiment_started".
	Knows when to arm, disarm, and fire (if applicable).
	"""
	def __init__(self) -> None:
		super(TriggeredSensor, self).__init__()

	def __repr__(self) -> str:
		return "TriggeredSensor({}, arming={}, disarming={}, firing={}"\
			.format(super(TriggeredSensor, self).__repr__(), self.arming(), self.disarming(), self.firing())
	def __str__(self) -> str: return repr(self)

	def arming(self) -> Set[Any]:
		raise NotImplementedError()
	def disarming(self) -> Set[Any]:
		raise NotImplementedError()
	def firing(self) -> Set[Any]:
		raise NotImplementedError()

	def trigger(self, trigger: Any):
		if trigger in self.arming(): self.arm()
		if trigger in self.firing(): self.fire()
		if trigger in self.disarming(): self.disarm()


__all__ = ['Sensor', 'PlottableSensor', 'TriggeredSensor']
