from __future__ import print_function

import math
from math import isnan, isinf
from datetime import datetime

__all__ = ['TimeRange', 'Runs']

class TimeRange(object):
    __slots__ = ('start', 'duration', 'peak', 'tags')

    def __init__(self, start, duration, peak=None, tags=None):
        self.start = start
        self.duration = duration
        self.peak = peak
        self.tags = tags

    def copy(self):
        return TimeRange(self.start, self.duration, self.peak, self.tags)

    def intersects_range(self, other):
        min_end = min(self.end, other.end)
        max_start = max(self.start, other.start)
        return max_start <= min_end

    def add_tag(self, tag):
        self.tags.add(tag)

    def add_tags(self, tags):
        self.tags.update(tags)

    @property
    def end(self):
        return self.start + self.duration

    @end.setter
    def end(self, value):
        self.duration = value - self.start

    def to_dict(self):
        return { 'start': self.start,
                 'duration': self.duration,
                 'peak': self.peak,
                 'tags': list(self.tags) if self.tags else [] }

    @classmethod
    def from_dict(cls, d):
        return cls(d['start'], d['duration'], d['peak'], set(d.get('tags', [])))

    def __repr__(self):
        peak_str = ''
        if self.peak is not None:
            peak_str = '; peak {:.2f}'.format(self.peak)

        tags_str = ''
        if self.tags is not None and len(self.tags) > 0:
            tags_str = '; tags ({})'.format(', '.join(self.tags))

        return '<TimeRange {:.2f} - {:.2f}; duration {:.2f}s{}{}>'.format(self.start / 1000., self.end / 1000., self.duration / 1000., peak_str, tags_str)

class Runs(object):
    def __init__(self, minimum_run_duration, maximum_gap_between_runs):
        self._minimum_run_duration = minimum_run_duration
        self._maximum_gap_between_runs = maximum_gap_between_runs
        self.runs = []
        self._current_run = None

    def copy(self):
        copy = Runs(self._minimum_run_duration, self._maximum_gap_between_runs)
        if self._current_run: copy._current_run = self._current_run.copy()
        copy.runs = [run.copy() for run in self.runs]
        return copy

    def add_run(self, start, duration, peak):
        # Extend or create a run
        if self._current_run is None:
            self._current_run = TimeRange(start, duration, peak)
        else:
            new_duration = (start - self._current_run.start) + duration
            new_peak = max(self._current_run.peak, peak)
            self._current_run.duration = new_duration
            self._current_run.peak = new_peak

    def add_gap(self, start, duration):
        if self._current_run is not None:
            # Are we still close enough to the end of the current run that we can overlook this gap?
            if start - self._current_run.end < self._maximum_gap_between_runs:
                return
            
            self.end_current_run()

    def end_current_run(self):
        # A gap terminates the current run. If it's long enough, add it to the runs array
        if self._current_run is not None and self._current_run.duration >= self._minimum_run_duration:
            self.runs.append(self._current_run)
        
        self._current_run = None

    def time_range_intersects_a_run(self, time_range):
        for run in self.runs:
            if run.start > time_range.end:
                # We've gone past all applicable ranges
                return False
            
            if time_range.intersects_range(run):
                return True
        
        return False

    def time_is_in_a_run(self, time):
        for run in self.runs:
            if time >= run.start:
                if time < run.end:
                    return True
                return False
        
        return False

    def normalize(self):
        # sorts runs based on start time and merges overlapping runs
        def normalize_runs(runs):
            if len(runs) <= 1: return runs

            run = runs[0]
            next_run = runs[1]
            if run.intersects_range(next_run):
                run.duration += next_run.duration
                run.peak = max(run.peak, next_run.peak)
                # todo: merge tags
                return normalize_runs([run] + runs[2:])
            
            return [run] + normalize_runs(runs[1:])
        
        sorted_runs = sorted(self.runs, key=lambda r: r.start)
        self.runs = normalize_runs(sorted_runs)

    def pad_runs(self, pre_padding, post_padding, max_duration):
        for run in self.runs:
            run.start = max(0, run.start - pre_padding)
            run.duration += pre_padding + post_padding
            if run.end > max_duration:
                run.duration = max_duration - run.start
        
        self.normalize()

    def to_dict(self):
        d = { 'minimum_run_duration': self._minimum_run_duration,
              'maximum_gap_between_runs': self._maximum_gap_between_runs,
              '_current_run': None,
              'runs': [r.to_dict() for r in self.runs] }
        if self._current_run is not None:
            d['_current_run'] = self._current_run.to_dict()
        
        return d

    @classmethod
    def from_dict(cls, d):
        runs = cls(d['minimum_run_duration'], d['maximum_gap_between_runs'])
        if d['_current_run'] is not None:
            runs._current_run = TimeRange.from_dict(d['_current_run'])
        runs.runs = map(lambda rd: TimeRange.from_dict(rd), d['runs'])
        return runs

    def __repr__(self):
        if len(self.runs) == 0: return '<Runs (empty)>'
        
        runs_reprs = '\n  '.join(map(repr, self.runs))
        total_duration_s = sum([run.duration for run in self.runs]) / 1000.
        duration_s = total_duration_s % 60
        duration_m = int(total_duration_s / 60)
        return '<Runs ({} runs; total duration {}:{:05.2f})>:\n  {}'.format(len(self.runs), duration_m, duration_s, runs_reprs)
