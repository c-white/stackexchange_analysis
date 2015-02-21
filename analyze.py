#!/usr/bin/python

"""
Program for analyzing Stackexchange answers.

Usage: Call this script from this directory:
    ./analyze.py -a <answer_file> -q <quality_file>
Alternatively (and in the case of the Python interpreter being elsewhere), call this script via Python:
    python analyze.py -a <answer_file> -q <quality_file>

Notes:
  - Designed and tested on Python 2.7
  - Creates/overwrites certain .png files in plots/ containing output visuals
  - Should use query http://data.stackexchange.com/physics/query/273688/scores-for-my-answers
    - Replace "physics" with another site if desired
    - Enter UserID, or append "?UserId=<user_id>" to URL
    - Run query
    - Download csv to data/<answer_file>
  - Should have matching quality data in data/<quality_file>
    - File format:
      - No header
      - <answer_id><whitespace><quality_score>
    - Quality score should be integer from 0 to 10 inclusive
    - Quality score is a subjective measure of how good an answer is
"""

# Python modules
import numpy as np
import argparse
import csv
import datetime

# Python plotting modules
import matplotlib
matplotlib.use('agg')
from matplotlib import rc
rc('text', usetex=True)
import matplotlib.pyplot as plt

# Main function
def main(**kwargs):

  # Parameters
  max_quality = 5
  plot_rows = 2
  plot_cols = 3
  intervals_per_decade = 4
  main_color = '#0099FF'
  zero_color = '#000066'
  x_label_factor = 0.95
  y_label_factor = 0.95
  x_pad = 20
  y_pad = 25
  bottom_margin = 0.1
  left_margin = 0.08

  # Read and organize data
  data_answers = read_answers(kwargs['answers'])
  data_quality = read_quality(kwargs['quality'])
  answer_scores,answer_dates,question_scores,question_dates,views,qualities = associate_data(data_answers, data_quality)

  # Bin data
  min_score = min(min(answer_scores), 0)
  max_score = max(answer_scores)
  max_log_boundary_index = int(np.ceil(intervals_per_decade * np.log10(max_score+0.5)))
  bins_lin = np.linspace(min_score-0.5, max_score+0.5, max_score-min_score+2)
  bins_lin = np.append(bins_lin, 10.0**(float(max_log_boundary_index)/float(intervals_per_decade)))
  bins_log = 10.0**(np.linspace(0.0, float(max_log_boundary_index), max_log_boundary_index+1) / intervals_per_decade)
  bins_log = np.insert(bins_log, 0, min_score-0.5)
  counts_lin = []
  counts_log = []
  max_counts_log = 0
  for quality in range(0,max_quality+1):
    counts_lin_local,_ = np.histogram(answer_scores[np.where(qualities == quality)[0]], bins=bins_lin)
    counts_lin.append(counts_lin_local)
    counts_log_local = np.zeros(len(bins_log)-1)
    for i in range(len(counts_log_local)):
      log_low = bins_log[i]
      log_high = bins_log[i+1]
      for j in range(len(bins_lin)-1):
        lin_low = bins_lin[j]
        lin_high = bins_lin[j+1]
        if lin_high <= log_low:
          continue
        if lin_low >= log_high:
          break
        covered_fraction = (min(lin_high, log_high) - max(lin_low, log_low)) / (lin_high - lin_low)
        counts_log_local[i] += covered_fraction * counts_lin_local[j]
    counts_log.append(counts_log_local)
    max_counts_log = max(max_counts_log, max(counts_log_local))

  # Plot data
  fig = plt.figure(figsize=(8,6))
  ax = fig.add_subplot(1, 1, 1)
  for axis in ['bottom', 'top', 'left', 'right']:
    ax.spines[axis].set_color('none')
  ax.tick_params(bottom='off', top='off', left='off', right='off')
  ax.tick_params(labelbottom='off', labeltop='off', labelleft='off', labelright='off')
  edges = np.linspace(2.0, float(len(bins_log)-1), len(bins_log)-2)
  edges = np.insert(edges, 0, 0.0)
  widths = np.ones_like(edges)
  colors = [zero_color] + (len(bins_log)-2) * [main_color]
  num_ticks = max_log_boundary_index / intervals_per_decade + 1
  x_tick_labels = []
  text_x = x_label_factor * (len(bins_log)-1)
  text_y = y_label_factor * max_counts_log
  for exponent in range(num_ticks+1):
    x_tick_labels.append('$10^'+str(exponent)+'$')
  x_tick_locations = np.linspace(2.0, (num_ticks-1)*intervals_per_decade+2.0, num_ticks)
  for quality in range(0,max_quality+1):
    fig.add_subplot(plot_rows, plot_cols, quality+1)
    plt.bar(edges, counts_log[quality], width=widths, bottom=0.0, color=colors)
    plt.xlim([0, len(bins_log)-1])
    plt.ylim([0, max_counts_log])
    plt.xticks(x_tick_locations, x_tick_labels)
    if quality % plot_cols == 0:  # left column of subplots
      plt.tick_params(axis='y', direction='out', right='off')
    else:
      plt.tick_params(axis='y', left='off', right='off', labelleft='off', labelright='off')
    if quality - max_quality > -plot_cols:  # bottom row of subplots
      plt.tick_params(axis='x', direction='out', top='off')
    else:
      plt.tick_params(axis='x', bottom='off', top='off', labelbottom='off', labeltop='off')
    plt.text(text_x, text_y, '$Q = '+str(quality)+'$', horizontalalignment='right', verticalalignment='top')
  ax.set_xlabel('Answer Score', labelpad=x_pad)
  ax.set_ylabel('Count', labelpad=y_pad)
  plt.tight_layout(w_pad=0.0, h_pad=0.0)
  fig.subplots_adjust(bottom=bottom_margin, left=left_margin)
  plt.savefig('plots/histogram.png')

# Function for reading in quality data
def read_quality(filename):
  data = {}
  with open(filename, 'r') as f:
    for line in f:
      split_line = line.split()
      data[split_line[0]] = split_line[1]
  return data

# Function for reading in votes data
def read_answers(filename):
  data = {}
  with open(filename) as f:
    reader = csv.DictReader(f)
    for row in reader:
      data[row['Id']] = row
  return data

# Function for associated two datasets based on ID's
def associate_data(answer_data, quality_data):
  answer_scores = []
  answer_dates = []
  question_scores = []
  question_dates = []
  views = []
  qualities = []
  for key,data in answer_data.iteritems():
    answer_scores.append(int(data['Answer Score']))
    answer_dates.append(datetime.datetime.strptime(data['Answer Date'], '%Y-%m-%d %H:%M:%S'))
    question_scores.append(int(data['Question Score']))
    question_dates.append(datetime.datetime.strptime(data['Question Date'], '%Y-%m-%d %H:%M:%S'))
    views.append(int(data['Views']))
    if key in quality_data:
      qualities.append(int(quality_data[key]))
    else:
      qualities.append(None)
  answer_scores = np.array(answer_scores)
  question_scores = np.array(question_scores)
  views = np.array(views)
  qualities = np.array(qualities)
  return answer_scores,answer_dates,question_scores,question_dates,views,qualities

# Execute main function
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-a', '--answers',
      type=str,
      required=True,
      help='name of comma-separated file in data/ holding answer information')
  parser.add_argument('-q', '--quality',
      type=str,
      required=True,
      help='name of whitespace-separated file in data/ holding quality information')
  args = parser.parse_args()
  main(**vars(args))
