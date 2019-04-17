#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

class TweetCleaner:
    #taken from https://stackoverflow.com/a/49146722
    def remove_emoji(self, string):
        emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', string)

    def load_stopwords(self, fname_list):
        stopwords_list = []
        for file in fname_list:
            with open(file, 'r', encoding='utf8') as f:
                stopwords_list.append(f.read().splitlines())
        #dirty workaround
        flat_list = [w for sub_sw in stopwords_list for w in sub_sw]
        return flat_list

    def clean_apostrophe_s(self, input):
        new_list = []
        for w in input.split(' '):
            if "'s" in w:
                new_list.append(w.split("'s")[0])
            else:
                new_list.append(w)
        return ' '.join(new_list)

    def standardize_quotes(self, input):
        input = input.replace("’", "'")

        new_list = []
        for w in input.split(' '):
            if w.startswith("'") or w.startswith("\""):
                w = w[1:]
            if w.endswith("'") or w.endswith("\""):
                w = w[:-1]
            new_list.append(w)

        return ' '.join(new_list)

    def remove_stopwords(self, input, stop_words):
        new_list = []
        for w in input.split(' '):
            if w.lower() not in stop_words:
                new_list.append(w)
        return ' '.join(new_list)

    #needs further investigation
    def remove_symbols(self, input):
        return re.sub('\?|\.|\!|\/|\;|\:|\´|\`|\*|\¨|\%|\(|\)|\&|\$|\=|\+|\,|\[|\]\'\"', '', input)

    def remove_rts(self, ldict, tweet):
        if tweet['text'][:4] == 'RT @':
            ldict.remove(tweet)


    def remove_urls(self, input):
        input = re.sub(r'pic.twitter\S+', '', input)
        return re.sub(r'http\S+', '', input)
