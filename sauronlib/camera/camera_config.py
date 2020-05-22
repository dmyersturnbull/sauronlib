from typing import Dict, Any, Optional

from sauronlib.camera import Roi


class CameraConfig:
	"""Configuration needed to start and run a camera.
	Only the settings needed for this purpose are required, though the ones defined here are expected to be required.
	Contains a dictionary 'extra_settings' to store any settings that are not expected to be required.
	"""
	def __init__(
			self,
			fps: int, roi: Roi,
			mode: Optional[str] = None, adaptor_name: Optional[str] = None, device_index: Optional[int] = None,
			exposure: Optional[float] = None, gain: Optional[float] = None,
			**kwargs
	):
		self.fps = fps
		self.roi = roi
		self.mode = mode
		self.adaptor_name = adaptor_name
		self.device_index = device_index
		self.exposure = exposure
		self.gain = gain
		self.__dict__.update(kwargs)

	def __repr__(self) -> str:
		return "CameraConfig({})".format(self.__dict__)

	def __str__(self) -> str: return str(self)


__all__ = ['CameraConfig']
