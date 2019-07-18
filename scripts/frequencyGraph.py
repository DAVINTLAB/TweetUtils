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
import collections
import matplotlib.pyplot as plt
import numpy as np

sys.path.append("..")

from modules.loader import Loader
from modules.cleaner import TweetCleaner

def add_args():
    parser = argparse.ArgumentParser(description='Created a File with frequency graph')
    parser.add_argument('-i', '--infile', metavar='', required=True, help='Input CSV file cleaned. Has to contain a key named user_id and created')
    parser.add_argument('-o', '--outfile', metavar='', default='output_default.txt', help='Filename for the resulting output. Default is "output_default.txt"')
    return parser.parse_args()



def createDict(infile):

    #read file with loader module
    loader = Loader()
    items = loader.read_file(infile)

    #create dict() 
    dic = collections.defaultdict(list)
    
    for tweet in items:
        aux = tweet['user_name']
        #Check if key exists in dictionary using in operator
        if aux in dic:
            dic[aux] = dic[aux] + 1
        else:
            dic[aux] = 1

    #sorted dictionary
    list_x =sorted(dic.items(), key=lambda kv: kv[1], reverse=True)
    return list_x


def createGraph(tupla, outfile):
    names = []
    values = []
    cont = 0
    save = {}
    qtd = 0 
    for fst, snd in tupla:
        names.append(cont)
        values.append(snd)
        if qtd < snd:
            qtd = snd
        save[fst] = (snd, cont)
        cont = cont + 1


    arq = open(outfile, 'w')
    arq.write('user_name --- (qtdTweet, LocalizacaoX)\n')
    for k,v in save.items():
        arq.write(str(k)+'\t'+str(v)+'\n')
    arq.close() 

    plt.plot(np.arange(len(names)), values)
    plt.ylabel('Numbers')
    plt.xlabel('Users')
    plt.title('Frequency Graph')
    plt.show()
    
def main():
    args = add_args()
    createGraph(createDict(args.infile), args.outfile)
    print('All Done.')

if __name__== "__main__":
    main()
