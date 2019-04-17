#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
import time
import argparse
import json
import tweepy

sys.path.append("..")

from modules.manager import TokenManager


def add_args():
    parser = argparse.ArgumentParser(description='Collects tweets from a user\'s profile in Twitter')
    parser.add_argument('-u', '--username', metavar='', required=True, help='Profile username to be collected')
    parser.add_argument('-o', '--outfile', metavar='', help='Filename for the resulting output. Default is "<profile username>.json"')
    return parser.parse_args()

def json_format(data_json, current_tweet):
    current_tweet['id'] = data_json.id
    current_tweet['created_at'] = data_json.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
    current_tweet['username'] = data_json.user.name
    try:
        #media = json.loads(data_json.entities['media'])
        current_tweet['media_type'] = data_json.entities['media'][0]['type']
        current_tweet['has_media'] = 'True'
        #print json.dumps(media)
    except:
        current_tweet['has_media'] = 'False'
        current_tweet['media_type'] = 'None'
    current_tweet['screen_name'] = data_json.user.screen_name
    current_tweet['retweet_count'] = data_json.retweet_count
    current_tweet['favorite_count'] = data_json.favorite_count
    current_tweet['text'] = data_json.text
    current_tweet['lang'] = data_json.lang
    return

def gather(api, args):
    try:
        user_id = api.get_user(args.username).id
    except tweepy.error.TweepError:
        print('User not found.')
        sys.exit(0)

    if args.outfile:
        fname = args.outfile + '.json'
        dataset_file = open(fname, 'w', encoding='utf8')
    else:
        fname = args.username + '.json'
        dataset_file = open(fname, 'w', encoding='utf8')

    dataset_file.write('[')
    current_tweet = {}
    dados = api.home_timeline()
    last_id = int(str(json.dumps(dados[0]._json))[55:74])
    counter = 0

    while True:
        try:
            new_tweets = api.user_timeline(id = user_id, count = 200, max_id=str(last_id-1))
            if not new_tweets:
                dataset_file.write(']')
                break
            for tweet in new_tweets:
                if counter != 0:
                    dataset_file.write(',')
                json_format(tweet, current_tweet)
                dataset_file.write(json.dumps(current_tweet, ensure_ascii=False))
                dataset_file.write('\n')
                counter+=1
                if sys.stdout.isatty():
                    print("\rNumber of tweets collected so far...: %i"%counter, end='\r', flush=True)
                else:
                    print(counter, end=' ', flush=True)

            last_id = new_tweets[-1].id
        except Exception as e:
            raise
    fim = time.time()
    print("\nAll done. Output written to " + fname)
    time.sleep(4.5)
    dataset_file.close()



def main():
    args = add_args()
    manager = TokenManager()
    api = manager.init_api()
    gather(api, args)


if __name__== "__main__":
    main()
