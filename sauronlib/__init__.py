import logging
from pathlib import Path
from typing import Sequence, Optional
from terminaltables import AsciiTable

logger = logging.getLogger('sauronlib')

# importlib.metadata is compat with Python 3.8 only
from importlib_metadata import PackageNotFoundError, metadata as __load

logger = logging.getLogger("sauronlib")

try:
    metadata = __load(Path(__file__).parent.name)
    __status__ = "Development"
    __copyright__ = "Copyright 2016–2020"
    __date__ = "2020-05-22"
    __uri__ = metadata["home-page"]
    __title__ = metadata["name"]
    __summary__ = metadata["summary"]
    __license__ = metadata["license"]
    __version__ = metadata["version"]
    __author__ = metadata["author"]
    __maintainer__ = metadata["maintainer"]
    __contact__ = metadata["maintainer"]
except PackageNotFoundError:
    logger.error("Failed to import from sauronlib", exc_info=True)


def stamp(dt):
	# https://bugs.python.org/issue19475
	return dt.isoformat(timespec='microseconds')

def show_table(headers: Sequence[str], rows: Sequence[Sequence[str]], title: Optional[str] = None) -> str:
	data = [headers]
	data.extend(rows)
	return AsciiTable(data, title=title).table

class ImmutableModificationError(Exception): pass

class Immutable:
	def __setattr__(self, *args):
		raise ImmutableModificationError()
	def __delattr__(self, *args):
		raise ImmutableModificationError()

class Mutable:
	pass

