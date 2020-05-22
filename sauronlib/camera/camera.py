from .camera_config import CameraConfig

class Camera:
	"""An abstract camera.
	Records video to a file for a specified  number of milliseconds.
	Undergoes the following events, in order:
		1. init() connects to the camera and starts any necessary engine.
		2. stream() starts capturing and streams the output.
		3. exit() disconnects the camera and closes any remaining streams.
	There is also a snapshot mode:
		1. init() connects to the camera and starts any necessary engine.
		2. snapshot() takes a single snapshot.
		3. exit() disconnects the camera and closes any remaining streams.
	Example usage:
		config = CameraConfigBuilder().mode(mode).device_index(1).build()
		with MyCameraImplementation(path, snaps, temp_dir, 1000, 10, config) as camera:
			camera.start()
			camera.stream()
			camera.finish()
	"""
	def __init__(
			self, config: CameraConfig, temp_dir: str,
	) -> None:
		self.config = config
		self.temp_dir = temp_dir

	def __enter__(self):
		self.init()
		return self

	def __exit__(self, type, value, traceback) -> None:
		self.exit()

	def init(self) -> None:
		"""Should raise MissingComponentException"""
		return None

	def exit(self) -> None:
		return None

	def stream(self, n_milliseconds: int, video_path: str, timestamps_path: str) -> None:
		raise NotImplementedError()

	def snapshot(self, image_path: str) -> None:
		raise NotImplementedError()


__all__ = ['Camera']
