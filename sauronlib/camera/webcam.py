from .camera import *

import cv2
from sauronlib import logger


class Webcam(Camera):

	def init(self):
		cap = cv2.VideoCapture(self.config.device_index)
		cap.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
		cap.set(3, self.config.roi.width())
		cap.set(4,self.config.roi.height())
		cap.set(15, self.config.exposure)
		for i in range(0, 18):
			try:
				logger.debug("Webcam {}={}".format(i, cap.get(i)))
			except:
				logger.debug("Failed to read webcam {}".format(i))
		self.cap = cap

	def stream(self, n_milliseconds: int, video_path: str, timestamps_path: str) -> None:
		raise NotImplementedError()  # TODO

	def snapshot(self, image_path: str) -> None:
		ret, frame = self.cap.read()
		cv2.imwrite(image_path, frame)


__all__ = ['Webcam']
