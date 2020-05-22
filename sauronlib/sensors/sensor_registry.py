from typing import Dict, List, Set, Any, Iterable, Union
from warnings import warn

from .sensor import Sensor, TriggeredSensor


class SensorRegistry:
	"""A collection of TriggeredSensors, which respond to triggers.
	Example usage:
		registry = SensorRegistry({'thermometer', 'photometer', 'microphone'}).add(Thermometer(), Photometer())
		registry.trigger('board_initialized')
		something_needed = get_something_needed()
		registry.add(Microphone(something_needed))
		registry.trigger('experiment_started').trigger('going_going_going')
		sleep(10)
		registry.trigger('all_done')
	"""
	def __init__(self, expected: Set[str]) -> None:
		self._expected = expected
		self._sensors = []  # type: List[TriggeredSensor]
		self._by_name = []  # type: Dict[str, List[TriggeredSensor]]

	def add(self, *sensors: TriggeredSensor):
		for sensor in sensors:
			if sensor.name() not in self._expected:
				warn("Sensor {} is unexpected".format(sensor))
			self._sensors.extend(sensor)
		self._by_name = {s.name(): [] for s in self._sensors}
		return self

	def remove(self, *sensors: TriggeredSensor):
		for sensor in sensors:
			self._sensors.remove(sensor)
		return self

	def armed(self) -> List[Sensor]:
		return [s for s in self._sensors if s.is_armed()]

	def unarmed(self) -> List[Sensor]:
		return [s for s in self._sensors if not s.is_armed()]

	def trigger(self, trigger: Any):
		for sensor in self._sensors:
			sensor.trigger(trigger)
		return self

	def __len__(self) -> int:
		return len(self._sensors)

	def __getitem__(self, name: Union[type, str, Sensor]) -> List[Sensor]:
		if isinstance(name, type): item = name.sensor_name()
		if isinstance(name, Sensor): name = name.name()
		return self._by_name[name]

	def __contains__(self, item: Union[type, str, Sensor]):
		if isinstance(item, type): item = item.sensor_name()
		if isinstance(item, Sensor): item = item.name()
		return item in self._by_name

	def __iadd__(self, other: TriggeredSensor):
		self.add(other)

	def __isub__(self, other: TriggeredSensor):
		self.remove(other)

	def __repr__(self) -> str:
		return "SensorRegistry({})".format(self._sensors)
	def __str__(self) -> str: return repr(self)


__all__ = ['SensorRegistry']
