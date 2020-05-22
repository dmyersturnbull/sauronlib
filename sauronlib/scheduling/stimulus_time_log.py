import datetime
from typing import Optional, List, Tuple, Union, Iterator

from sauronlib import logger, stamp
from sauronlib.stimulus import *


class StimulusTimeRecord:
	def __init__(self, stimulus: Stimulus, real_timestamp: datetime.datetime) -> None:
		self.stimulus = stimulus
		self.real_timestamp = real_timestamp

	def delta_timestamp(self) -> datetime.datetime:
		return StimulusTimeRecord.calc_delta(self.real_timestamp)

	@staticmethod
	def calc_delta(real_timestamp: datetime.datetime) -> datetime.datetime:
		return real_timestamp + datetime.timedelta(microseconds=0)


class StimulusTimeLog:

	def __init__(self, records: Optional[List[StimulusTimeRecord]] = None) -> None:
		self.records = [] if records is None else records
		self.start_time = None  # type: datetime
		self.end_time = None  # type: datetime

	def start(self) -> None:
		self.start_time = datetime.datetime.now()

	def finish_now(self) -> None:
		self.end_time = datetime.datetime.now()

	def finish_future(self, dt: datetime.datetime) -> None:
		self.end_time = dt

	def __iter__(self) -> Iterator[StimulusTimeRecord]:
		return iter(self.records)

	def __len__(self) -> int:
		return len(self.records)

	def __getitem__(self, index: Union[int, slice]) -> Union[StimulusTimeRecord, List[StimulusTimeRecord]]:
		if isinstance(index, slice):
			return [self.records[i] for i in range(index.start, index.stop, index.step)]
		else: return self.records[index]

	def append(self, record: StimulusTimeRecord) -> None:
		self.records.append(record)

	def write(self, log_file: str) -> None:
		logger.debug("Writing stimulus times.")
		with open(log_file, 'w') as file:
			file.write('datetime,id,intensity\n')
			start_stamp = stamp(StimulusTimeRecord.calc_delta(self.start_time))
			file.write('{},0,0\n'.format(start_stamp))
			for record in self:
				current_stamp = stamp(record.delta_timestamp())
				if record.stimulus is not StimulusType.MARKER:
					file.write("{},{},{}\n".format(current_stamp, record.stimulus.key.id, record.stimulus.byte_intensity))
			end_stamp = stamp(StimulusTimeRecord.calc_delta(self.end_time))
			file.write('{},0,0'.format(end_stamp))
		logger.debug("Finished writing stimulus times.")


__all__ = ['StimulusTimeRecord', 'StimulusTimeLog']
