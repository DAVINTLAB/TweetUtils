#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import ijson
import json
import csv
import re
import pathlib
import math
from collections import Counter

sys.path.append("..")

from modules.loader import Loader
from modules.cleaner import TweetCleaner

def add_args():
    parser = argparse.ArgumentParser(description='Created a File with bigram or trigram')
    parser.add_argument('-i', '--infile', metavar='', required=True, help='Input CSV file cleaned. Has to contain a key named text')
    parser.add_argument('-o', '--outfile', metavar='', default='output_default.csv', help='Filename for the resulting output. Default is "output_default.csv"')
    parser.add_argument('-t', '--type', metavar='', required=True, help='Input type to be created bigram (b) or trigram (t).')
    return parser.parse_args()

def write_csv(outfile, data):
    with open(outfile, 'w', encoding='utf8') as outfile:
        outfile.write("text; size\n")
        for word,counted in data:
            if counted <= 0:
                continue
            outfile.write(word.replace('_', ' '))
            outfile.write('; ')
            outfile.write(str(math.ceil(counted)))
            outfile.write('\n')
    print('All done.')

def write_file(infile, outfile, data):
    if outfile != 'output_clean.json':
        extension = pathlib.Path(outfile).suffix
    else:
        extension = pathlib.Path(infile).suffix
        outfile = 'output_clean' + extension

    if extension == '.csv':
        write_csv(outfile, data)
    else:
        print ('Output file must be in CSV format\nQuitting...')

def createBigramTrigram(infile, outfile, type):

    #read file with loader module
    loader = Loader()
    items = loader.read_file(infile)

    plt = []

    #create bigram or trigram
    for tweet in items:
        if type == 'b':
            plt.append(bigramas(tweet['text']))
        else:
            plt.append(trigramas(tweet['text']))

    #Pass all strings list to a single string
    palavras = ' '
    for i in range(len(plt)):
        for j in range(len(plt[i])):
            palavras += plt[i][j].replace('\n',' ').replace('\t','')+' '

    #Formatting 
    count = {}
    for word in palavras.split(" "):
            if len(word) < 0:
                continue
            if word not in count:
                count[word] = 0
            count[word]+=1

    l = sorted(count.items(), key=lambda x: -x[1])

    write_file(infile, outfile, l)


def bigramas(words):
    bigrams = []
    listAux = str(words).split()
    for i in range(1, len(listAux)):
        if (i == len(listAux)-2):
            break
        else:
            bigrama_obs = listAux[i-1]+'_'+listAux[i]
            bigrams.append(bigrama_obs)
    return bigrams

def trigramas(words):
    trigrams = []
    listAux = str(words).split()
    for i in range(2,len(listAux)):
        if (i == len(listAux)-3):
            break
        else:
            trigrama_obs = listAux[i-2] + '_' + listAux[i-1] + '_' + listAux[i]
            trigrams.append(trigrama_obs)
    return trigrams

def main():
    args = add_args()
    createBigramTrigram(args.infile, args.outfile, args.type)


if __name__== "__main__":
    main()
