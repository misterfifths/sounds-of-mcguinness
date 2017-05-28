#!/usr/bin/env python

from __future__ import print_function
from pydub import AudioSegment
from lib import *
import json

run_padding = 0  # applied to beginning & end of each run
run_crossfade = 0  # not extra; taken from the run + padding
peak_min = 76

def runs_from_json_file(filename):
    with open(filename, 'r') as f:
        d = json.load(f)
        return Runs.from_dict(d)

def make_supercut(basename):
    runs = runs_from_json_file('runs_' + basename + '.json')
    audio = AudioSegment.from_wav('filtered_' + basename + '.wav')

    filtered_runs = []
    quiet_runs = 0
    wind_runs = 0
    for run in runs.runs:
        if run.peak < peak_min:
            quiet_runs += 1
            continue
        if 'wind' in run.tags:
            wind_runs += 1
            continue
        if 'gate' in run.tags:
            continue
        
        filtered_runs.append(run)
    
    print(quiet_runs, 'quiet runs /', wind_runs, 'wind runs')

    runs.runs = filtered_runs

    runs.pad_runs(run_padding, run_padding, len(audio))

    supercut = None
    for run in runs.runs:
        if supercut is None:
            supercut = audio[run.start:run.end]
        else:
            chunk = audio[run.start:run.end]
            supercut = supercut.append(chunk, crossfade=run_crossfade)
    
    return supercut


if __name__ == '__main__':
    from os.path import basename, splitext
    import sys

    ubercut = None
    for filename in sys.argv[1:]:
        file_datetime = splitext(basename(filename))[0][5:]
        supercut = make_supercut(file_datetime)
        if ubercut is None:
            ubercut = supercut
        elif supercut is not None:
            ubercut = ubercut.append(supercut, crossfade=run_crossfade)
    
    ubercut.export('ubercut.mp3', format='mp3')