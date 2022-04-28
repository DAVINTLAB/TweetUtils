#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import json
import csv
import pathlib

sys.path.append("..")

from modules.loader import Loader
from modules.cleaner import TweetCleaner

def add_args():
    parser = argparse.ArgumentParser(description='Removes stopwords, non-twitter symbols, URLs, and emoji from JSON datasets.')
    parser.add_argument('-i', '--infile', metavar='', required=True, help='Input JSON file to be cleaned. Has to contain a key named text')
    parser.add_argument('-o', '--outfile', metavar='', default='output_clean.json', help='Filename for the resulting output. Default is "output_clean" in the input file extension format')
    parser.add_argument('-s', '--stopwords', metavar='', nargs='+', default = ['./stopwords/stopwords_en.txt'], help='Filename (or path) for the list of stopwords. Default is "stopwords/stopwords_en.txt"')
    parser.add_argument('-e', '--emoji', action="store_true", help='Retains emoji contained in the input file')
    parser.add_argument('-rt', '--removeRT', action="store_true", help='Exclude tweets deemed as retweets from the input file (e.g tweets starting with \"RT @\")')
    return parser.parse_args()


def write_json(outfile, data):
    json_string = json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)
    with open(outfile, 'w', encoding='utf8') as f:
        f.write(json_string)
    sys.stdout.write('All done. File written to ' + outfile)

def write_csv(outfile, data):
    keys = data[0].keys()
    with open(outfile, 'w', encoding='utf8') as f:
        dict_writer = csv.DictWriter(f, keys, extrasaction='ignore', lineterminator='\n')
        dict_writer.writeheader()
        dict_writer.writerows(data)
    sys.stdout.write('All done. File written to ' + outfile)

def write_file(infile, outfile, data):
    if outfile != 'output_clean.json':
        extension = pathlib.Path(outfile).suffix
    else:
        extension = pathlib.Path(infile).suffix
        outfile = 'output_clean' + extension

    if extension == '.csv':
        write_csv(outfile, data)
    elif extension == '.json':
        write_json(outfile, data)
    else:
        sys.stdout.write('Output file must be in CSV or JSON format\nQuitting...')

def sanitize(infile, outfile, stopwords, emoji, rt):
    #initialize cleaner and load stopwords

    cleaner = TweetCleaner()
    stopwords = cleaner.load_stopwords(stopwords)

    #read file with loader module
    loader = Loader()
    items = loader.read_file(infile)

    #remove stopwords and emoji from tweets
    for tweet in items:
        tweet['text'] = cleaner.standardize_quotes(tweet['text'])
        tweet['text'] = cleaner.clean_apostrophe_s(tweet['text'])
        tweet['text'] = cleaner.remove_urls(tweet['text'])
        tweet['text'] = cleaner.remove_symbols(tweet['text'])
        tweet['text'] = cleaner.remove_stopwords(tweet['text'], stopwords)
        if not emoji:
            tweet['text'] = cleaner.remove_emoji(tweet['text'])
        if rt:
            cleaner.remove_rts(items, tweet)

    write_file(infile, outfile, items)


def main():
    args = add_args()
    sanitize(args.infile, args.outfile, args.stopwords, args.emoji, args.removeRT)



if __name__== "__main__":
    main()
