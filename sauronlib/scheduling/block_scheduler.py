import logging, typing
from typing import List, Optional, Union, Any

import pydub
import numpy as np

from sauronlib.stimulus import StimulusType, Stimulus
from sauronlib.scheduling.schedule import Schedule
from sauronlib.audio_info import AudioInfo


class Block:
	def __init__(self, name: str, start: int, frames: np.array, audio_always_native_length: bool = False):
		self.name = name
		self.start = start
		self.frames = frames
		self.audio_always_native_length = audio_always_native_length

	def __repr__(self):
		return "Block({} (start:{}{}): {}".format(self.name, self.start, ', always native audio length' if self.audio_always_native_length else '', self.frames)
	def __str__(self): return repr(self)


class BlockScheduler:

	def __init__(self, total_ms: int):
		self.total_ms = total_ms
		self._chained = []  # type: List[typing.Tuple[int, Union[str, Stimulus]]]
		self._blocks = []  # type: List[Block]

	def __repr__(self):
		return "BlockScheduler({}, total={})".format(self._blocks, self.total_ms)

	def __str__(self): return repr(self)

	def build(self) -> Schedule:
		x = self._chained.copy()
		self._chained = None
		return Schedule(x, [(b.start, b.name) for b in self._blocks], self.total_ms)

	def append(self, stimulus_name: str, stimulus_key: Any, audio_obj: Optional[pydub.AudioSegment], blocks: List[Block]):
		#
		self._blocks.extend(blocks)
		#
		prev_value = 0
		prev_index = 0
		index = None
		#
		for block in blocks:
			# start of assay / block
			self._chained.append((
				block.start, block.name
			))
			# so that we can track the length, write the previous change when the next change is encountered
			# also, write the final change at the end
			logging.debug("Appending block {} of length {} (audio_always_native_length={})".format(block.name, len(block.frames), block.audio_always_native_length))
			#
			if index is not None and block.start != index + 1 and audio_obj is None:
				self._append(index, 0, None, block.audio_always_native_length, stimulus_name, stimulus_key, audio_obj)
				prev_value = 0
			#
			for mini_index, value in enumerate(block.frames):
				index = block.start + mini_index
				if value != prev_value:
					if prev_index > 0:
						self._append(prev_index, prev_value, index - prev_index, block.audio_always_native_length, stimulus_name, audio_obj)
					prev_index = index
					prev_value = value
			#
			if index is not None:
				self._append(prev_index, prev_value, index - prev_index, block.audio_always_native_length, stimulus_name, audio_obj)
		# we want a final stop at the end of the block
		if index is not None and audio_obj is None:
			self._append(index, 0, None, False, stimulus_name, stimulus_key, audio_obj)  # chirp=True or chirp=False should be fine
		return self

	def _append(self, ms: int, val: int, time_since: Optional[int], chirp: bool, stimulus_name: str, stimulus_key: Any, audio_obj: Optional[AudioInfo]) -> None:
		"""
		:param ms: The current ms
		:param val: The value to change to
		:param time_since: The ms since the last change
		:param chirp: Treat all audio as native-length regardless of how long the stimulus_frames are applied; for legacy assays
		"""
		# set length to None (native length) for legacy assays because they don't use the definition audio length==1 <==> play exact length
		duration_ms = None if chirp else time_since
		if duration_ms == 1: duration_ms = None
		audio_obj = AudioInfo.build(audio_obj.name, audio_obj.wave_obj, duration_ms, val) if (audio_obj is not None) else None
		built_stim = Stimulus(stimulus_name, stimulus_key, val, audio_obj, StimulusType.AUDIO)
		if built_stim.stim_type is not StimulusType.AUDIO or built_stim.byte_intensity > 0:
			self._chained.append((
				ms, built_stim
			))


__all__ = ['Block', 'BlockScheduler']