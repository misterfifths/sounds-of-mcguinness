# Analysis Scripts

This directory contains a bunch of Python scripts for analyzing and visualizing the sound files captured in the [iOS app](../NoiseRecorder).

# Requirements

- Python 2.7
- Probably only works on OSX; didn't try elsewhere
- The `pip` modules in `requirements.txt`:
    - [Pydub](http://pydub.com/)
    - [aubio](https://aubio.org/)
    - [PyAudio](https://pypi.python.org/pypi/PyAudio/) - see [notes here](https://gist.github.com/jiaaro/9767512210a1d80a8a0d) for installing in OSX
    - [numpy](https://docs.scipy.org/doc/numpy/reference/)
    - [matplotlib](http://matplotlib.org/)
    - [readchar](https://pypi.python.org/pypi/readchar)
- You should probably be a good person and use a [virtualenv](https://virtualenv.pypa.io/en/stable/)
- [FFmpeg](https://ffmpeg.org/), easily installed via [Homebrew](https://brew.sh/): `brew install ffmpeg`

### Use

So, assuming you have a bunch of AAC files from the iOS app, this is the workflow for ingesting those files:

1. First, we need to apply an [A-weighting](https://en.wikipedia.org/wiki/A-weighting) filter to the AAC files and convert them to WAV for ease of use. The `a_weight.py` script does this:

    ```sh
    $ ./a_weight.py *.aac
    ```
2. Now, we need to crunch some statistics (peak, mean, and min volume) and find runs of loudness in the WAV files. That's what `stat_and_runs.py` does. Feed it the `filtered_` WAV files, and it will generate JSON files with statistics and runs:

    ```sh
    $ ./stats_and_runs.py filtered_*.wav
    ```

3. We can now optionally listen to and manually tag the runs. At the moment, things tagged "wind" and "gate" are excluded from the supercut. The `tagger.py` script does this by adding tags to the runs JSON files:

    ```sh
    $ ./tagger.py runs_*.json
    ```

4. Making an audio supercut of loud noises is now possible with the `supercutter.py` script. Open it up to tweak options, and run it with the `runs_` JSON files. It will generate an MP3 in the current directory:

    ```sh
    $ ./supercutter.py runs_*.json
    ```

5. Finally, we can create graphs with the statistical data. The `graph_maker.py` script will make one graph per day, and one large graph containing all days. These will be exported as PNGs in the current directory.

    ```sh
    $ ./graph_maker.py stats_*.json
    ```

### Technical Details

We're mainly using Pydub to process the files due to its ease of use. However, since it lacks an A-weighting filter, we're using aubio for that piece.

Again, not much magic here. The scripts are all pretty messy, but hopefully short enough to follow.
