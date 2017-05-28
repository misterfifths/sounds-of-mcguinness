#!/usr/bin/env python

from __future__ import print_function
from pydub import AudioSegment
import pydub.playback as playback
from lib import *
import json
from readchar import readchar

run_padding = 1 * 1000

def runs_from_json_file(filename):
    with open(filename, 'r') as f:
        d = json.load(f)
        return Runs.from_dict(d)

def main(basename):
    print('> ', basename)
    runs_filename = 'runs_' + basename + '.json'
    runs = runs_from_json_file(runs_filename)
    audio = AudioSegment.from_wav('filtered_' + basename + '.wav')

    for i, run in enumerate(runs.runs):
        padded_start = max(0, run.start - run_padding)
        padded_end = min(len(audio), run.start + run_padding)
        chunk = audio[padded_start:padded_end]

        print('{}/{} [e]mergency, [w]ind, [j]ake brake, [h]orn, [g]ate, [r]eplay, [O]ther: '.format(i + 1, len(runs.runs)), end='')
        playback.play(chunk)

        tag = None
        while tag is None:
            tag = readchar()
            if tag == 'r':
                playback.play(chunk)
                tag = None
            elif tag == 'q': exit()
            elif tag == '\r': tag = ''
            elif tag == 'h': tag = 'horn'
            elif tag == 'w': tag = 'wind'
            elif tag == 'e': tag = 'emergency'
            elif tag == 'j': tag = 'jake brake'
            elif tag == 'g': tag = 'gate'
            else: tag = None
        
        if tag != '': run.add_tag(tag)
        print('\n   ', repr(run))
    
    with open(runs_filename, 'w') as f:
        json.dump(runs.to_dict(), f)

if __name__ == '__main__':
    from os.path import basename, splitext
    import sys

    ubercut = None
    for filename in sys.argv[1:]:
        file_datetime = splitext(basename(filename))[0][5:]
        main(file_datetime)
