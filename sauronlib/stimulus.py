from enum import Enum
from typing import Union, Optional, Any

from sauronlib.audio_info import AudioInfo


class StimulusType(Enum):
	ANALOG = 1
	DIGITAL = 2
	AUDIO = 3
	MARKER = 4


class Stimulus:
	"""The application of an Arduino or audio stimulus at a specified byte intensity (or volume).
	"""
	def __init__(
			self,
			key: Any,
			name: str,
			byte_intensity: Union[None, int, float, bool],
			audio_obj: Optional[AudioInfo],
			stim_type: StimulusType
	) -> None:
		self.key = key
		self.name = name
		self.byte_intensity = byte_intensity
		self.audio_obj = audio_obj
		self.stim_type = stim_type
		assert (audio_obj is None) != (stim_type is StimulusType.AUDIO)
		if self.stim_type == StimulusType.AUDIO:
			self.intensity = audio_obj.intensity
		else:
			self.intensity = byte_intensity

	def __str__(self) -> str: return repr(self)
	def __repr__(self) -> str:
		return "Stimulus({}{}={})".format(self.key, '' if self.audio_obj is None else '(' + str(self.audio_obj) + ')', self.intensity)

	def is_audio(self) -> bool:
		return self.stim_type == StimulusType.AUDIO
	def is_analog(self) -> bool:
		return self.stim_type == StimulusType.ANALOG
	def is_digital(self) -> bool:
		return self.stim_type == StimulusType.DIGITAL


__all__ = ['Stimulus', 'StimulusType']
