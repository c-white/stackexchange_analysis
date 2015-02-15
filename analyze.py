#!/usr/bin/python

"""
Program for analyzing Stackexchange answers.

Usage: Call this script from this directory:
    ./analyze.py
Alternatively (and in the case of the Python interpreter being elsewhere), call this script via Python:
    python analyze.py

Notes:
  - Designed and tested on Python 2.7.
"""

# Python modules
import argparse

# Main function
def main(**kwargs):
  exit()

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
