import wave
from datetime import datetime
from os.path import dirname

import numpy as np
import pyaudio
from scipy.io import wavfile
from hipsterplot import HipsterPlotter

from klgists.files import make_dirs

from sauronlib import logger
from sauronlib.sensors.sensor import Sensor
from sauronlib import stamp


class Microphone(Sensor):
	"""A microphone that records a WAV file to a file.
	Runs for a specified number of milliseconds. fire() opens and closes the stream.
	"""

	def __init__(self, output_path: str, timestamp_file_path: str, sample_rate: int, frames_per_buffer: int) -> None:
		super(Microphone, self).__init__()
		self.output_path = output_path
		self.timestamp_file_path = timestamp_file_path
		self.sample_rate = sample_rate
		self.frames_per_buffer = frames_per_buffer
		self.audio_format = pyaudio.paInt32
		self.channels = 1
		self._stream = None
		self._p = None
		self._timestamps = None
		self._frames = None
		self.log_file = None
		super(Microphone, self).__init__()

	def _arm(self, **kwargs) -> None:
		logger.info("Recording {} to {}".format(self.name(), self.output_path))
		make_dirs(dirname(self.log_file))
		self.timestamps = []
		self.frames = []
		try:
			self._p = pyaudio.PyAudio()
			self._stream = self._p.open(
				format=self.audio_format,
				channels=self.channels,
				rate=self.sample_rate,
				input=True,
				frames_per_buffer=self.frames_per_buffer
			)
		except Exception as e:
			logger.fatal("Failed to start microphone.")
			#warn_user("Failed to start microphone.")
			raise e

	def _fire(self) -> None:
		# TODO exception handling got a bit much here
		try:
			while not self.should_kill[0]:
				data = self._stream.read(self.frames_per_buffer)
				self.frames.append(data)
				self.timestamps.append(datetime.now())
		except Exception as e:
			logger.fatal("Microphone failed while capturing")
			#warn_user("Microphone failed while capturing")
			raise e
		self.save()
		self._kill()

	def disarm(self):
		self.should_kill[0] = True

	def save(self):
		try:
			logger.info("Writing microphone data...")
			logger.debug("Writing microphone timestamps")
			with open(self.timestamp_file_path, 'w') as f:
				for ts in self.timestamps:
					f.write(stamp(ts) + '\n')
			logger.debug("Writing microphone WAV data")
			wf = wave.open(self.log_file, 'wb')
			try:
				wf.setnchannels(self.channels)
				wf.setsampwidth(self._p.get_sample_size(self.audio_format))
				wf.setframerate(self.sample_rate)
				wf.writeframes(b''.join(self.frames))
			finally:
				wf.close()
		except Exception as e:
			#warn_user("Microphone failed while writing the .wav file")
			raise e
		logger.info("Finished writing microphone data.")

	def plot(self):
		logger.debug("Plotting microphone data (may take a couple minutes)...")
		with open(self.output_path, 'rb') as f:
			self.sampling_rate, data = wavfile.read(f)
			ms = np.array([i / self.sampling_rate * 1000 for i in range(0, len(data))])
		low_x = self.timestamps[0].strftime('%H:%M:%S')
		high_x = self.timestamps[-1].strftime('%H:%M:%S')
		s = HipsterPlotter(num_y_chars=10).plot(data, title=self.name(), low_x_label=low_x, high_x_label=high_x)
		with open(self.output_path + '.plot.txt', 'w', encoding="utf8") as f:
			f.write(s)
		return s

	def _kill(self):
		logger.info("Terminating microphone...")
		logger.debug("Ending microphone process")
		try:
			self._p.terminate()  # failing here is probably bad
		except Exception as b:
			logger.warning("Failed to terminate microphone process")
			logger.debug(b, exc_info=True)
		logger.debug("Ending microphone stream")
		try:
			self._stream.stop_stream()
		except Exception as b:
			logger.warning("Failed to stop microphone stream")
			logger.debug(b, exc_info=True)
		logger.debug("Closing microphone stream")
		try:
			self._stream.close()
		except Exception as b:
			logger.warning("Failed to close microphone process")
			logger.debug(b, exc_info=True)
		self._p = None  # ; self._thread = None
		logger.debug("Microphone exited")
		logger.info("Terminated microphone.")


__all__ = ['Microphone']
