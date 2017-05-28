#!/usr/bin/env python

from __future__ import print_function
import math
from math import isnan, isinf
import json
from lib import *
from pydub import AudioSegment
import numpy as np


magic_dbfs_to_dba_constant = 93.5

stats_window = 10 * 1000

min_dBA_for_loud_run =  70
minimum_run_duration = 0.1 * 1000
maximum_gap_between_runs = 0.5 * 1000


def get_dBAs(audio):
    dBAs = np.empty(len(audio))
    for pos_ms in xrange(0, len(audio)):
        sample = audio[pos_ms]
        dBFS = sample.dBFS
        dBA = 0
        if not isnan(dBFS) and not isinf(dBFS):
            dBA = dBFS + magic_dbfs_to_dba_constant
        
        dBAs[pos_ms] = dBA
    
    return dBAs

def get_stats(dBAs, stats_window):
    stats_buckets = int(math.floor(len(dBAs) / stats_window))
    means = np.empty(stats_buckets)
    peaks = np.empty(stats_buckets)
    valleys = np.empty(stats_buckets)

    for i in range(0, stats_buckets):
        audio_start_idx = i * stats_window
        dBAs_slice = dBAs[audio_start_idx:audio_start_idx + stats_window]
        peaks[i] = dBAs_slice.max()
        valleys[i] = dBAs_slice.min()
        means[i] = dBAs_slice.mean()
    
    return (means, peaks, valleys)

def main(basename):
    print('\n> ' + basename)
    source = AudioSegment.from_wav('filtered_' + basename + '.wav')

    duration_ms = len(source)
    pos_step = 1

    runs = Runs(minimum_run_duration, maximum_gap_between_runs)

    dBAs = get_dBAs(source)

    means, peaks, valleys = get_stats(dBAs, stats_window)

    file_datetime = datetime_from_filename_string(basename)

    stats_dicts = []
    i = 0
    for start, end in iter_time_buckets(file_datetime, duration_ms, stats_window):
        stat = Stat(start, end, basename, means[i], peaks[i], valleys[i])
        stats_dicts.append(stat.to_dict())
        i += 1
    
    with open('stats_' + basename + '.json', 'w') as f:
        json.dump(stats_dicts, f)

    for pos_ms in xrange(0, duration_ms, pos_step):
        dBA = dBAs[pos_ms]
        if dBA > min_dBA_for_loud_run:
            runs.add_run(pos_ms, pos_step, dBA)
        else:
            runs.add_gap(pos_ms, pos_step)
    
    runs.end_current_run()
    
    with open('runs_' + basename + '.json', 'w') as f:
        json.dump(runs.to_dict(), f)


if __name__ == '__main__':
    from os.path import basename, splitext
    import sys

    for filename in sys.argv[1:]:
        file_datetime = splitext(basename(filename))[0][9:]
        main(file_datetime)
