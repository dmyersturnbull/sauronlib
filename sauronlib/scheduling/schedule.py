from typing import List, Union
import typing
from datetime import timedelta

import numpy as np

from sauronlib import logger, show_table
from sauronlib.stimulus import Stimulus, StimulusType

class Schedule:

	def __init__(self, stimulus_list: List[typing.Tuple[int, Union[str, Stimulus]]], assay_positions: List[typing.Tuple[int, str]], total_ms: int):
		self.stimulus_list = stimulus_list
		self.assay_positions = assay_positions
		self.total_ms = total_ms

	def n_events(self) -> int:
		return len([1 for t in self.stimulus_list if isinstance(t[1], Stimulus)])

	def pretty_print_list(self) -> str:
		def tabify(index, stimulus) -> str:
			# TODO stimulus.key.name
			return (
				str(index).ljust(8)
				+ str(stimulus.key.name).ljust(20)
				+ str(round(stimulus.intensity, 2)).ljust(8)
				+ str('-' if stimulus.audio_obj is None else stimulus.audio_obj.duration_ms).ljust(8)
			)
		header = 'ms'.ljust(8) + 'stimulus'.ljust(20) + 'value'.ljust(8) + 'duration(ms)'.ljust(8)
		return '\n' + header + '\n' + '-'*(8+20+8+8) + '\n'\
			+ '\n'.join([
				tabify(e[0], e[1])
				for e in self.stimulus_list if not isinstance(e[1], str)
			]
		)

	def pretty_print_assays(self) -> str:
		def simpu(i):
			i = int(np.round(i / 1000))
			return str(timedelta(seconds=i))
		# TODO
		#return show_table(
		#	['assay', 'start', 'length'],
		#	[[p.assay.name, simpu(p.start), simpu(p.assay.length)] for t, s in self.assay_positions]
		#)


__all__ = ['Schedule']
