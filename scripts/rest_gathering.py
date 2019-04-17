#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
import time
import argparse
import json
import tweepy
import pandas as pd
import datetime

sys.path.append("..")

from modules.manager import TokenManager


def add_args():
    parser = argparse.ArgumentParser(description='Collects tweets from keywords in a date range, or the maximum limited allowed at the moment.')
    parser.add_argument('-q', '--query', metavar='', required=True, help='A UTF-8 encoded search query of 500 characters maximum. For operators reference, please refer to https://developer.twitter.com/en/docs/tweets/rules-and-filtering/overview/standard-operators.html')
    parser.add_argument('-s', '--since', metavar='', required=True, help='Returns results that are more recent than the specified date (UTC time). Expected format: "YYYY-MM-DD HH:MM"')
    parser.add_argument('-u', '--until', metavar='', required=True, help='Returns results that are older than  the specified date (UTC time). Expected format: "YYYY-MM-DD HH:MM"')
    parser.add_argument('-o', '--outfile', metavar='', default='outfile.json', help='Filename for the resulting output. Default is "<keywords>.json"')
    return parser.parse_args()


def find_id(api, date, query):
    date_until = date
    date_until += datetime.timedelta(days=1)
    query += ' since:' + date.strftime('%Y-%m-%d') + ' until:' + date_until.strftime('%Y-%m-%d')

    current = api.search(q = query, count=100, result_type="recent", include_entities=True)[0]
    last_id = current.id

    while True:
        try:
            new_tweets = api.search(q = query, count=100, include_entities=True, max_id=str(last_id-1))
            if not new_tweets:
                break
            for tweet in new_tweets:
                if abs((date - tweet.created_at).total_seconds()) <= abs((date - current.created_at).total_seconds()):
                    current = tweet
                else:
                    return current.id
            last_id = new_tweets[-1].id
        except Exception as e:
            #continue
            raise
        #time.sleep(4.5)


def json_format(data_json):
    current_tweet = {}
    current_tweet['id'] = data_json.id
    current_tweet['created_at'] = data_json.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
    current_tweet['userid'] = data_json.user.id
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
    return current_tweet


def gather(api, query, s_id, last_id, outfile):
    #dirty workaround
    last_id+=1
    counter = 0

    with open(outfile, 'w',  encoding='utf8') as f:
        f.write('[\n')
        while True:
            try:
                new_tweets = api.search(q = query, count=100, include_entities=True, since_id=s_id, max_id=str(last_id-1))
                if not new_tweets:
                    print ('\nAll done! Finishing...')
                    break
                for tweet in new_tweets:
                    formatted = json_format(tweet)
                    f.write(json.dumps(formatted, ensure_ascii=False))
                    f.write(',\n')

                    counter+=1

                    if sys.stdout.isatty():
                        print("\rNumber of tweets collected so far...: %i"%counter, end='', flush=True)
                    else:
                        print(counter, end=' ', flush=True)

                last_id = new_tweets[-1].id
            except Exception as e:
                #continue
                raise


def date_adjust(api, since, until, query):
    now = datetime.datetime.utcnow()
    id_since = None

    if until > now:
        print("Warning: 'until' parameter is newer than UTC datetime now. Defaulting to UTC now instead...")
        until = now
    if since < (now - datetime.timedelta(days = 10)):
        print("Warning: 'since' parameter is older than 10 days. Any tweet older than 9 days will not be retrieved.")
        since = None

    print('Dates validated!\nFinding date ranges. This may take a while...')
    id_until = find_id(api, until, query)

    if since != None:
        id_since = find_id(api, since, query)
    print ('Found date ranges!')

    return (id_since, id_until)


def date_check(since, until):
    now = datetime.datetime.utcnow()

    if since > until:
        print ("'since' parameter cannot be newer than 'until'.\nQuitting...")
        sys.exit(0)
    elif until < (now - datetime.timedelta(days = 10)):
        print ("'until' parameter cannot be older than 10 days as per Twitter API regulations.\nQuitting...")
        sys.exit(0)



def main():
    args = add_args()

    date_until = pd.to_datetime(args.until)
    date_since = pd.to_datetime(args.since)

    date_check(date_since, date_until)

    manager = TokenManager()
    api = manager.init_api()

    (id_since, id_until) = date_adjust(api, date_since, date_until, args.query)

    gather(api, args.query, id_since, id_until, args.outfile)

if __name__== "__main__":
    main()