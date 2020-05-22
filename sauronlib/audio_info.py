import math, logging
from typing import Union, Optional

import pydub
import simpleaudio as sa

from klgists.common.operators import approxeq

class BadVolumeException(Exception): pass
class BadAudioLengthException(Exception): pass


class AudioInfo:
	"""All information necessary to play an audio file.
	Most importantly, contains a static build() method that will alter the volume extend and truncate an audio segment
	as needed for a specified length.
	"""

	def __init__(self, name: str, wave_obj: sa.WaveObject, duration_ms: Optional[float], intensity: float):
		self.name = name
		self.wave_obj = wave_obj
		self.duration_ms = duration_ms
		self.intensity = intensity

	def __str__(self):
		return "AudioInfo({}ms@{}dB)".format(self.duration_ms, round(self.intensity, 5))

	@staticmethod
	def build(
			name: str, song: pydub.AudioSegment,
			applied_length: Optional[int]=None, volume: int=255, volume_floor: int = -50,
			bytes_per_sample: int=2, sample_rate: int=44100
	):

		if applied_length is not None and applied_length < 0:
			raise BadAudioLengthException("The length is {} but cannot be negative".format(applied_length))
		if volume < 0 or volume > 255:
			raise BadVolumeException("The volume is {} but must be 0–255".format(volume))

		if applied_length is None:
			resized = song
		else:
			n_repeats = math.ceil(applied_length / len(song))
			resized = (song * n_repeats)[0:applied_length]

		if volume == 0 or applied_length == 0:
			final = pydub.AudioSegment.silent(duration=0.5)
		else:
			final = resized + (volume * (volume_floor / 255) - volume_floor)
			if applied_length is not None:
				assert len(resized) << approxeq >> applied_length or applied_length == 1,\
						"The actual audio stimulus length is {}, but the length in stimulus_frames is {}".format(len(resized), applied_length)

		play_obj = sa.WaveObject(final.raw_data, 1, bytes_per_sample, sample_rate)
		return AudioInfo(name, play_obj, applied_length, volume)


__all__ = ['AudioInfo']
