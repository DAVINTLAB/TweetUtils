#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import tweepy
import argparse
import json
import datetime


def add_args():
    parser = argparse.ArgumentParser(description='Coleta tweets de acordo com a query, data e limites.')
    parser.add_argument('-q', '--query', metavar='', required=True)
    parser.add_argument('-k', '--key', metavar='', required=True, help='Chave (Bearer key) para a extração de dados do Twitter')
    parser.add_argument('-s', '--start_time', metavar='', required=True, help='"YYYY-MM-DDTHH:mmZ"  UTC')
    parser.add_argument('-u', '--end_time', metavar='', required=True, help='"YYYY-MM-DDTHH:mmZ" UTC')
    parser.add_argument('-m', '--maxtweets', metavar='', type=int, default=100)
    parser.add_argument('-o', '--outfile', metavar='', default="output.json")
    return parser.parse_args()

def date_check(since, until):
    now = datetime.datetime.utcnow()

    if since > until:
        sys.stdout.write("'since' parameter cannot be newer than 'until'.\nQuitting...")
        sys.exit(0)

def main():
    args = add_args()
    client = tweepy.Client(args.key, wait_on_rate_limit=True)

    date_check(datetime.datetime.strptime(args.start_time, '%Y-%m-%dT%H:%MZ'), datetime.datetime.strptime(args.end_time, '%Y-%m-%dT%H:%MZ'))
    args.start_time = args.start_time[:-1]+':00Z'
    args.end_time = args.end_time[:-1]+':00Z'

    arq = open(args.outfile, 'w')
    
    arq.write("[\n")
    counter = 1

    for tweet in tweepy.Paginator(client.search_recent_tweets, args.query, max_results=args.maxtweets, end_time=args.end_time, start_time=args.start_time, tweet_fields=['created_at', 'lang', 'public_metrics', 'author_id']).flatten():
        id = tweet.id
        text = tweet.text
        created_at = tweet.created_at
        lang = tweet.lang
        author_id = tweet.author_id
        rt_count = tweet.public_metrics['retweet_count']
        line = {'id' : id, 'text' : text, 'created_at' : created_at, 'lang' : lang, 'author_id' : author_id, 'retweet_count' : rt_count}
        line['created_at'] = line['created_at'].strftime('%Y-%m-%dT%H:%M:%SZ')
        
        if counter == 1:
            arq.write(json.dumps(line)+'\n')

        else:
            arq.write(','+json.dumps(line)+'\n')

        sys.stdout.write("\rNumber of tweets collected so far...: %i"%counter)
        sys.stdout.flush()
        counter += 1

    arq.write("]")
    arq.close()
    sys.stdout.write('\nAll done! Finishing...')

if __name__== "__main__":
    main()