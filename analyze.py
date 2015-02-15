#!/usr/bin/python

"""
Program for analyzing Stackexchange answers.

Usage: Call this script from this directory:
      ./analyze.py -q <quality_file> -v <votes_file>
  Alternatively (and in the case of the Python interpreter being elsewhere), call this script via Python:
      python analyze.py -q <quality_file> -v <votes_file>

Notes:
  - Designed and tested on Python 2.7.
"""

# Python modules
import numpy as np
import argparse
import csv

# Main function
def main(**kwargs):
  
  # Read and organize data
  data_quality = read_data('data/'+kwargs['quality'])
  data_votes = read_data('data/'+kwargs['votes'])
  quality,votes = sort_data(data_quality, data_votes)

# Function for reading in text file with data
def read_data(filename):
  data = {}
  with open(filename, 'r') as f:
    for line in f:
      split_line = line.split()
      data[split_line[0]] = int(split_line[1])
  return data

# Function for associated two datasets based on ID's
def sort_data(data_1, data_2):
  vals_1 = []
  vals_2 = []
  for key,val in data_1.iteritems():
    vals_1.append(val)
    vals_2.append(data_2[key])
  return np.array(vals_1),np.array(vals_2)

# Execute main function
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-q', '--quality',
      type=str,
      required=True,
      help='name of file in data/ holding quality information')
  parser.add_argument('-v', '--votes',
      type=str,
      required=True,
      help='name of file in data/ holding votes information')
  args = parser.parse_args()
  main(**vars(args))
