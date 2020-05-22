from typing import List
import subprocess
from sauronlib.camera.camera import Camera
from sauronlib.camera.camera_config import CameraConfig
from sauronlib import logger


class ExternalCommandCamera(Camera):

	def __init__(
			self, config: CameraConfig, temp_dir: str,
			stdout_path: str, stderr_path: str
	) -> None:
		super().__init__(config, temp_dir)
		self.stdout_path = stdout_path
		self.stderr_path = stderr_path

	def _stream_executable(self) -> str:
		raise NotImplementedError()

	def _snapshot_executable(self) -> str:
		raise NotImplementedError()

	def stream(self, n_milliseconds: int, video_path: str, timestamps_path: str) -> None:
		logger.info("Camera will capture for {}ms. Starting!".format(n_milliseconds))
		cmd = self.build_cmd(n_milliseconds, video_path, timestamps_path)
		logger.info("Running {}".format(cmd))
		try:
			with open(self.stdout_path, 'a') as out:
				with open(self.stderr_path, 'a') as err:
					subprocess.run(cmd, stdout=out, stderr=err)
		except Exception as e:
			logger.fatal("Failed running {}".format(self._stream_executable()))
			raise e
		logger.info("Camera finished capturing.")

	def build_cmd(self, n_milliseconds: int, video_path: str, timestamps_path: str) -> List[str]:
		return [
			self._stream_executable(),
			str(n_milliseconds),
			str(self.config.fps),
			str(self.config.roi.x0), str(self.config.roi.y0), str(self.config.roi.width()), str(self.config.roi.height()),
			timestamps_path,
			video_path
		]

	def snapshot(self, image_path: str) -> None:
		with open(self.stdout_path, 'a') as out:
			with open(self.stderr_path, 'a') as err:
				# TODO fix
				subprocess.run([self._snapshot_executable(), image_path, '0'], stdout=out, stderr=err)


__all__ = ['ExternalCommandCamera']
