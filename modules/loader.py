#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv
import json
import ijson
import pathlib

class Loader:
    def detect_delimiter(self, csv_file):
        with open(csv_file, 'r',  encoding='utf8') as csvfile:
            temp_lines = csvfile.readline() + '\n' + csvfile.readline()
            dialect = csv.Sniffer().sniff(temp_lines, delimiters=',;|')
            return dialect

    def load_json(self, fname):
        with open(fname, 'r', encoding='utf8') as f:
            objects = ijson.items(f, 'item')
            items = list(objects)
            print ('File loaded successfully! Processing...')
            return items

    def load_csv(self, fname):
        dia = self.detect_delimiter(fname)
        with open(fname, 'r',  encoding='utf8') as csvfile:
            dict = csv.DictReader(csvfile, dialect=dia)
            items = list(dict)
            print ('File loaded successfully! Processing...')
            return items

    def read_file(self, fname):
        extension = pathlib.Path(fname).suffix
        if extension == '.csv':
            print('Loading CSV file...')
            return self.load_csv(fname)
        elif extension ==  '.json':
            print('Loading JSON file...')
            return self.load_json(fname)
        else:
            print ('Input file must be in CSV or JSON format\nQuitting...')
            sys.exit(0)
