#!/usr/bin/env python

from __future__ import print_function

import json
from lib import *
import matplotlib.pyplot as plt
import matplotlib.text
import matplotlib.patheffects as path_effects
import numpy as np

plt.rcParams['font.family'] = 'Avenir'

stat_window_length_s = 10
background_color = '#e3e8ef'
gray_color = '#666666'

legal_limits = [#('Cars (old)', 70),
                ('Cars', 76),
                ('Motorcycles', 82),
                ('Trucks', 86),
                ('WHO-recommended max for sleep', 30)]
legal_limit_color = '#8e658a'

y_axis_limits = [25, 95]
y_axis_first_tick = 30


def stats_from_json_file(filename):
    with open(filename, 'r') as f:
        stat_dicts = json.load(f)
        return [Stat.from_dict(stat_dict) for stat_dict in stat_dicts]

def split_on_start_date(stats):
    current_datetime = None
    current_list = []
    split_stats = []
    for stat in stats:
        if current_datetime is None:
            current_datetime = stat.start
            current_list.append(stat)
            continue
        
        next_datetime = stat.start
        if next_datetime.date() == current_datetime.date():
            current_list.append(stat)
        else:
            current_datetime = next_datetime
            split_stats.append(current_list)
            current_list = []
    
    if len(current_list) > 0:
        split_stats.append(current_list)
    
    return split_stats

def collect_and_merge_stats(stats_for_day, merge_window):
    means = []
    peaks = []
    valleys = []

    for start_idx in xrange(0, len(stats_for_day), merge_window):
        stat_chunk = stats_for_day[start_idx:start_idx + merge_window]
        merged_stat = stat_chunk[0]
        for stat in stat_chunk[1:]:
            merged_stat.merge_with(stat)
        
        means.append(merged_stat.mean)
        peaks.append(merged_stat.peak)
        valleys.append(merged_stat.valley)
    
    return (means, peaks, valleys)

def make_graph(stats, graph_window_length_s, figure_size):
    first_date = stats[0][0].start
    last_date = stats[-1][-1].end
    duration = (last_date - first_date).total_seconds()

    flattened_stats = []
    for day_stats in stats:
        flattened_stats += day_stats

    means, peaks, valleys = collect_and_merge_stats(flattened_stats, graph_window_length_s / stat_window_length_s)  # collect_and_merge_stats thinks in numbers of stat samples to merge, so graph_widnow_length / stat_window_length results in the right number of merges
    times = np.arange(0, duration, graph_window_length_s)[0:len(means)]  # slice is correcting for potential off-by-one when division is imperfect

    print(first_date, last_date)
    
    fig = plt.figure(figsize=figure_size)
    ax = fig.add_subplot(111)

    ax.plot(times, means, linewidth=0.7, label='Mean', zorder=10)
    ax.plot(times, peaks, linewidth=0.7, label='Peak', zorder=10)

    for label, dBA in legal_limits:
        ax.axhline(dBA, linewidth=0.2, alpha=0.75, color=legal_limit_color, zorder=0)
        text = ax.text(850, dBA + 0.5, label, size='x-small', alpha=0.75, zorder=20)
        text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='white'),
                               path_effects.Normal()])

    if len(stats) > 1:
        # more than one day? 6 AM & PM
        tick_times = range(6 * 60 * 60, int(duration), 12 * 60 * 60)
    else:
        # one day? every other hour
        tick_times = range(0, int(duration), 2 * 60 * 60)
    tick_labels = []
    for tick_time in tick_times:
        hour = (tick_time / 60 / 60) % 24
        if hour == 0: label = '12am'
        elif hour < 12: label = str(hour) + 'am'
        elif hour == 12: label = '12pm'
        else: label = str(hour - 12) + 'pm'
        tick_labels.append(label)
    ax.set_xticks(tick_times)
    ax.set_xticklabels(tick_labels, weight='light')
    
    ax.set_xticks(range(1 * 60 * 60, int(duration), 1 * 60 * 60), True) # minor, every-hour ticks

    ax.set_yticks(range(y_axis_first_tick, y_axis_limits[1], 10))
    
    ax.set_xlabel('Time', labelpad=5, size='large', weight='light', color=gray_color)
    ax.set_ylabel('dBA', size='large', weight='light', color=gray_color)

    ax.set_xlim([0, times[-1]])
    ax.set_ylim(y_axis_limits)

    if len(stats) > 1:
        # more than one day?
        # day labels at the top, and divider lines per day
        top_axis = ax.twiny()
        top_axis.tick_params(length=0)  # hide top ticks
        top_axis.set_xlim(ax.get_xlim())
        top_axis.set_xticks(range(12 * 60 * 60, int(duration), 24 * 60 * 60))  # noons
        day_tick_labels = []
        for day_stats in stats:
            first_date = day_stats[0].start
            date_str = first_date.strftime('%A, %-m-%-d-%Y')
            day_tick_labels.append(date_str)
        top_axis.set_xticklabels(day_tick_labels, weight='medium', size='large')

        for midnight in range(24 * 60 * 60, int(duration), 24 * 60 * 60):
            ax.axvline(midnight, linewidth=0.2, alpha=0.75, color=gray_color)
    else:
        # one day? just a big title
        date_str = first_date.strftime('%A, %-m-%-d-%Y')
        plt.title(date_str, size='x-large', weight='medium')

    legend = ax.legend(loc='lower right', fancybox=False, framealpha=1, facecolor='#f8f8f8', edgecolor=gray_color, fontsize='small', ncol=2, borderpad=0.5, handlelength=0.75, handleheight=0, borderaxespad=0.7, columnspacing=1, handletextpad=0.25)
    legend.get_frame().set_linewidth(0.2)  # set legend border line thickness
    for legend_handle in legend.legendHandles:
        legend_handle.set_linewidth(1.5)  # set thickness of colored lines in legend

    fig.tight_layout()
    return fig

def make_daily_graphs(stats_by_date):
    for day_stats in stats_by_date:
        fig = make_graph([day_stats], 15 * 60, (6, 4))
        date_str = day_stats[0].start.strftime('%m-%d-%Y')
        fig.savefig(date_str, dpi=300)
        plt.close()

def make_big_graph(stats_by_date):
    fig = make_graph(stats_by_date, 30 * 60, (18, 4))
    fig.savefig('all-together', dpi=300)
    plt.close()


if __name__ == '__main__':
    import sys

    all_stats = []

    for filename in sys.argv[1:]:
        all_stats += stats_from_json_file(filename)
    
    all_stats.sort(key=lambda sd: sd.start)
    stats_by_date = split_on_start_date(all_stats)

    # first & last day are incomplete
    del stats_by_date[0]
    del stats_by_date[-1]

    print('data from', len(stats_by_date), 'dates')

    make_daily_graphs(stats_by_date)
    make_big_graph(stats_by_date)
