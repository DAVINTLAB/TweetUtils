#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import tweepy
import argparse
import json

def add_args():
    parser = argparse.ArgumentParser(description='Coleta tweets de acordo com a query, data e limites.')
    parser.add_argument('-u', '--user', metavar='', required=True)
    parser.add_argument('-k', '--key', metavar='', required=True, help='Chave (Bearer key) para a extração de dados do Twitter')
    parser.add_argument('-o', '--outfile', metavar='', default="output_profile.json")
    return parser.parse_args()


def main():
    args = add_args()
    arq = open(args.outfile, 'w')
    client = tweepy.Client(args.key)

    arq.write("[\n")
    counter = 1

    for tweet in tweepy.Paginator(client.get_users_tweets, args.user, max_results=100, tweet_fields=['created_at', 'lang', 'public_metrics', 'author_id']).flatten():
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