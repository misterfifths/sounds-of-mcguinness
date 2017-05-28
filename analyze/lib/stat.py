from __future__ import print_function
from utils import datetime_from_str, datetime_str

__all__ = ['Stat']

class Stat(object):
    __slots__ = ('start', 'end', 'source', 'mean', 'peak', 'valley')

    def __init__(self, start, end, source, mean, peak, valley):
        self.start = start
        self.end = end
        self.source = source
        self.mean = mean
        self.peak = peak
        self.valley = valley
    
    @property
    def duration(self):
        return (self.end - self.start).total_seconds()
    
    def _intersects(self, other):
        min_end = min(self.end, other.end)
        max_start = max(self.start, other.start)
        return max_start <= min_end
    
    def merge_with(self, other):
        if not self._intersects(other):
            if self.source == other.source:
                print('Merging non-overlapping Stat instances!\n  {}\n  {}'.format(repr(self), repr(other)))
            else:
                print('Merging non-overlapping Stat instances from different sources. Bound to happen.')
        
        self.start = min(self.start, other.start)
        self.end = max(self.end, other.end)
        self.peak = max(self.peak, other.peak)
        if self.valley == 0: self.valley = other.valley
        elif other.valley != 0: self.valley = min(self.valley, other.valley)

        unmeaned_sum = self.mean * self.duration + other.mean * other.duration
        self.mean = unmeaned_sum / (self.duration + other.duration)

    def to_dict(self):
        return { 'start': datetime_str(self.start),
                 'end': datetime_str(self.end),
                 'source': self.source,
                 'mean': self.mean,
                 'peak': self.peak,
                 'valley': self.valley }
    
    @classmethod
    def from_dict(cls, d):
        return cls(datetime_from_str(d['start']),
                   datetime_from_str(d['end']),
                   d['source'],
                   d['mean'],
                   d['peak'],
                   d['valley'])
    
    def __repr__(self):
        return '<Stat ({} - {}; duration {}s)>'.format(datetime_str(self.start), datetime_str(self.end), self.duration)