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
import matplotlib.pyplot as plt

# Main function
def main(**kwargs):
  
  # Read and organize data
  data_answers = read_answers('data/'+kwargs['answers'])
  data_quality = read_quality('data/'+kwargs['quality'])
  answer_scores,answer_dates,question_scores,question_dates,views,qualities = associate_data(data_answers, data_quality)

  # Plot data
  plt.scatter(qualities, answer_scores)
  plt.savefig('plots/quality_votes.png')

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
