#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import argparse

sys.path.append("..")

from modules.loader import Loader
from modules.cleaner import TweetCleaner


def add_args():
    parser = argparse.ArgumentParser(description='Generates a summary of the data contained in a Tweet dataset.')
    parser.add_argument('-i', '--infile', metavar='', required=True, help='Filename for the input JSON or CSV file')
    parser.add_argument('-dc', '--displaycount', type=int, default=10, metavar='', help='Display limit for most mentioned words, users and hashtags. Default is 10.')
    parser.add_argument('-o', '--outfile', metavar='', default='report.txt', help='Filename for the resulting output. Default is "report.txt"')
    return parser.parse_args()


def get_username_key(tweet):
    if 'username' in tweet:
        return 'username'
    elif 'screen_name' in tweet:
        return 'screen_name'
    elif 'user_name' in tweet:
        return 'user_name'
    else:
        print('Warning: username key does not exist.')
        return None


def format_print_tweet(tweet, username_key):
    #test which exists
    if username_key:
        return '\n\t@' + tweet[username_key] + '\n\t' + tweet['text'] + '\n\t' + tweet['retweets'] + ' retweets\n'
    else:
        return '\n\t' + tweet['text'] + '\n\t' + tweet['retweets'] + ' retweets\n'

def report(infile, outfile, displaycount):
    #initialize cleaner and load stopwords
    cleaner = TweetCleaner()
    stopwords = cleaner.load_stopwords([os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'modules', 'stopwords', 'stopwords_pt-br.txt')), os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'modules', 'stopwords', 'stopwords_en.txt'))])

    #read file with loader module
    sys.stdout.write('Reading file. This may take a while...'+"\n")
    sys.stdout.flush()
    #print('Reading file. This may take a while...')
    loader = Loader()
    items = loader.read_file(infile)
    sys.stdout.write('File read successfully!\nProcessing the summary...'+"\n")
    sys.stdout.flush()
    #print('File read successfully!\nProcessing the summary...')

    if 'text' not in items[0]:
        print("Warning: 'text' key is required.\nTerminating...")
        sys.exit(0)

    tweet_count = len(items)

    summary = "File name: " + infile + '\n'
    summary += "Tweet count: " + str(tweet_count) + "\n\n"

    if 'created_at' in items[0]:
        #created_at exists
        date_upper = items[0]['created_at']
        date_lower = items[tweet_count - 1]['created_at']

        summary += "Most recent tweet: " + date_upper + "\n"
        summary += "Oldest tweet: " + date_lower + "\n"
    elif 'date' in items[0]:
        date_upper = items[0]['date']
        date_lower = items[tweet_count - 1]['date']

        summary += "Most recent tweet: " + date_upper + "\n"
        summary += "Oldest tweet: " + date_lower + "\n"
    else:
          summary += "Warning: 'created_at' or 'date' key does not exist. Date range information cannot be fetched."

    username_key = get_username_key(items[0])

    if 'retweets' in items[0]:
        summary+='\nTop retweeted tweets:\n'
        cont = 0
        for tweet in sorted(items, reverse=True, key = lambda i: i['retweets']):
            if 'RT @' not in tweet['text'] and cont < displaycount:
                summary+= format_print_tweet(tweet, username_key)
                cont+=1
            if cont>=10:
                break


    word_list = []
    hashtag_list = []
    user_list = []

    for tweet in items:
        tweet['text'] = cleaner.standardize_quotes(tweet['text'])
        tweet['text'] = cleaner.clean_apostrophe_s(tweet['text'])
        tweet['text'] = cleaner.remove_urls(tweet['text'])
        tweet['text'] = cleaner.remove_symbols(tweet['text'])
        tweet['text'] = cleaner.remove_stopwords(tweet['text'], stopwords)
        tweet['text'] = cleaner.remove_emoji(tweet['text'])
        tweet['text'] = tweet['text'].lower()

    for tweet in items:
        #print(re.findall(r'#\w+', tweet['text']))
        hashtag_list += re.findall(r'#\w+', tweet['text'])
        user_list += re.findall(r'@\w+', tweet['text'])
        word_list += re.findall(r'\b\w+', tweet['text'])


    word_dict = {}
    hashtag_dict = {}
    user_dict = {}

    for hashtag in hashtag_list:
        if hashtag in hashtag_dict:
            hashtag_dict[hashtag] += 1
        else:
            hashtag_dict[hashtag] = 1

    for user in user_list:
        if user in user_dict:
            user_dict[user] += 1
        else:
            user_dict[user] = 1

    for word in word_list:
        if word in word_dict:
            word_dict[word] += 1
        else:
            word_dict[word] = 1


    summary+='\n\nWord ranking:\n\n'
    count = 0
    for key, value in sorted(list(word_dict.items()), reverse=True, key=lambda k_v: (k_v[1],k_v[0])):
         if count < displaycount:
             summary+= '\t%s: %s\n' % (key, value)
         count +=1

    summary+='\nUser ranking:\n\n'
    count = 0
    for key, value in sorted(list(user_dict.items()), reverse=True, key=lambda k_v: (k_v[1],k_v[0])):
         if count < displaycount:
             summary+= '\t%s: %s\n' % (key, value)
         count +=1


    count = 0
    summary+='\nHashtag ranking:\n\n'
    for key, value in sorted(list(hashtag_dict.items()), reverse=True, key=lambda k_v: (k_v[1],k_v[0])):
         if count < displaycount:
             summary+= '\t%s: %s\n' % (key, value)
         count +=1

    with open(outfile, 'w', encoding='utf8') as f:
        f.write(summary)

    sys.stdout.write('Succesfully wrote file to ' + outfile + '!'+"\n")
    sys.stdout.flush()
    #print('Succesfully wrote file to ' + outfile + '!')


def main(args):
    #args = add_args()
    report(args.infile, args.outfile, args.displaycount)

if __name__== "__main__":
    args = add_args()
    main(args)
