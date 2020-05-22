
class Roi:

	def __init__(self, x0: int, y0: int, x1: int, y1: int) -> None:
		self.x0 = x0
		self.y0 = y0
		self.x1 = x1
		self.y1 = y1

	def width(self) -> int:
		return self.x1 - self.x0

	def height(self) -> int:
		return self.y1 - self.y0

	def n_pixels(self) -> int:
		return (self.x1 - self.x0) * (self.y1 - self.y0)

	def __repr__(self) -> str:
		return "({},{})→({},{})".format(self.x0, self.y0, self.x1, self.y1)

	def __str__(self) -> str:
		return repr(self)

__all__ = ['Roi']
