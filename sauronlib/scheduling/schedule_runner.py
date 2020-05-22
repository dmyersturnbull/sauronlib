import datetime
import typing
from time import monotonic
from typing import Optional, List, Tuple, Union, Iterator, Callable

from asyncio import LifoQueue

from sauronx.core.sx_logger import logger
from sauronlib.scheduling.schedule import *
from sauronlib.scheduling.stimulus_time_log import *
from sauronlib.stimulus import *


class ScheduleRunner:
	"""
	This class is itself a queue: It will drop elements out of Schedule.queue as they are taken.
	"""
	def __init__(self, schedule: Schedule) -> None:
		"""Stimulus_list is in MILLISECONDS."""
		self.stimulus_list = schedule.stimulus_list
		self.queue = LifoQueue()
		self.time_range = range(0, len(self.stimulus_list))
		self.n_ms_total = schedule.total_ms
		# sorting on tuples apparently sorts by the first index first
		for index_ms, stimulus in sorted(schedule.stimulus_list, key=lambda x: x[0], reverse=True):
			self.queue.put_nowait((index_ms / 1000, stimulus))

	def get_nowait(self) -> typing.Tuple[int, Stimulus]:
		return self.queue.get_nowait()

	def run(
			self,
			write_callback: Callable[[Stimulus], None],
			audio_callback: Callable[[Stimulus], None]
	) -> StimulusTimeLog:
		"""Runs the stimulus schedule immediately.
		This runs the scheduled stimuli and blocks. Does not sleep.
		:param write_callback: Example: board.write
		:param audio_callback: Example: global_audio.play
		"""

		logger.info("Battery will run for {}ms. Starting!".format(self.n_ms_total))
		stimulus_time_log = StimulusTimeLog()
		stimulus_time_log.start()  # This is totally fine: It happens at time 0 in the stimulus_list AND the full battery.

		t0 = monotonic()
		for _ in self.time_range:
			scheduled_seconds, stimulus = self.get_nowait()
			while monotonic() - t0 < scheduled_seconds: pass

			# Use self._board.digital_write and analog_write because we don't want to perform checks (for performance)
			if stimulus is StimulusType.MARKER:
				logger.info("Starting: {}".format(stimulus.name))
				continue
			elif stimulus.is_digital() or stimulus.is_analog():
				write_callback(stimulus)
			elif stimulus.is_audio():
				audio_callback(stimulus)  # volume is handled internally
			else:
				raise ValueError("Invalid stimulus type %s!" % stimulus.stim_type)

			stimulus_time_log.append(StimulusTimeRecord(stimulus, datetime.datetime.now()))

		# This is critical. Otherwise, the StimulusTimeLog will finish() at the time the last stimulus is applied, not the time the battery ends
		# TODO double-check
		#while monotonic() - t0 < self.n_ms_total / 1000: pass
		offset_ms = datetime.timedelta(milliseconds = self.n_ms_total - monotonic() + t0)
		if offset_ms.microseconds < 0:
			logger.warning("Stimuli finished too late: {}ms after".format(offset_ms))
			offset_ms = 0
		stimulus_time_log.finish_future(datetime.datetime.now() + offset_ms)
		return stimulus_time_log  # for trimming camera frames



__all__ = ['ScheduleRunner']
