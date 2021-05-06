#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
import os
import time
import argparse
import json
import tweepy
import pandas as pd
import datetime
import pathlib
from math import inf

sys.path.append("..")

from modules.manager import TokenManager


def add_args():
    parser = argparse.ArgumentParser(description='Collects tweets from keywords in a date range, or the maximum limited allowed at the moment.')
    parser.add_argument('-q', '--query', metavar='', required=True, help='A UTF-8 encoded search query of 500 characters maximum. For operators reference, please refer to https://developer.twitter.com/en/docs/tweets/rules-and-filtering/overview/standard-operators.html')
    parser.add_argument('-s', '--since', metavar='', required=True, help='Returns results that are more recent than the specified tweet ID')
    parser.add_argument('-u', '--until', metavar='', required=True, help='Returns results that are older than the specified date tweet ID')
    parser.add_argument('-m', '--maxtweets', metavar='', default=inf, type=int, help='Stops the gathering when the max specified number is reached.')
    parser.add_argument('-t', '--toptweets', action="store_true", help='Returns top retweet tweets first. maxtweets argument has needs to be set.')
    parser.add_argument('-o', '--outfile', metavar='', help='Filename for the resulting output. Default is "<first_keyword>.csv"')
    return parser.parse_args()


def find_id(api, date, query):
    date_until = date
    date_until += datetime.timedelta(days=1)
    query += ' since:' + date.strftime('%Y-%m-%d') + ' until:' + date_until.strftime('%Y-%m-%d')

    current = api.search(q = query, count=100, result_type="recent", include_entities=True)[0]
    last_id = current.id

    while True:
        try:
            new_tweets = api.search(q = query, count=100, result_type="recent", tweet_mode="extended", include_entities=True, max_id=str(last_id-1))
            if not new_tweets:
                if current != None:
                    return (current.id)
                break
            for tweet in new_tweets:
                if abs((date - tweet.created_at).total_seconds()) <= abs((date - current.created_at).total_seconds()):
                    current = tweet
                else:
                    return (current.id)
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
    current_tweet['text'] = data_json.full_text
    current_tweet['lang'] = data_json.lang
    return current_tweet


def gather(api, query, s_id, last_id, outfile, maxtweets, toptweets):
    #dirty workaround
    last_id+=1
    counter = 0

    extension = pathlib.Path(outfile).suffix
    if toptweets:
        rtype = 'popular'
    else:
        rtype = 'recent'

    print(rtype)

    with open(outfile, 'w',  encoding='utf8') as f:
        if extension == '.csv':
            f.write('id,created_at,userid,username,media_type,has_media,screen_name,retweet_count,favorite_count,text,lang\n')
        elif extension == '.json':
            f.write('[\n')
        while True:
            try:
                new_tweets = api.search(q = query, count=100, include_entities=True, result_type=rtype, tweet_mode='extended', since_id=s_id, max_id=str(last_id-1))
                if not new_tweets:
                    print ('\nAll done! Finishing...')
                    break
                for tweet in new_tweets:
                    formatted = json_format(tweet)
                    if extension == '.json':
                        f.write(json.dumps(formatted, ensure_ascii=False))
                        f.write(',\n')
                    elif extension == '.csv':
                        formatted['text'] = ' '.join([line.strip() for line in formatted['text'].strip().splitlines()])
                        formatted['text'] = '"' + formatted['text'] + '"'
                        df = pd.DataFrame(formatted, index=[0])
                        csv_string = df.to_csv(header=False, index=False)
                        csv_string = ' '.join([line.strip() for line in csv_string.strip().splitlines()])
                        f.write(csv_string + '\n')

                    counter+=1

                    if sys.stdout.isatty():
                        print("\rNumber of tweets collected so far...: %i"%counter, end='', flush=True)
                    else:
                        print(counter, end=' ', flush=True)

                    if counter >= maxtweets:
                        break

                last_id = new_tweets[-1].id
            except Exception as e:
                #continue
                raise

        if extension == '.json':
            f.seek(f.tell() - 2, os.SEEK_SET)
            f.write("\n]")


def date_adjust(api, since, until, query):
    now = datetime.datetime.utcnow()

    if until > now:
        print("Warning: 'until' parameter is newer than UTC datetime now. Defaulting to UTC now instead...")
        until = now
    if since < (now - datetime.timedelta(days = 8)):
        print("Warning: 'since' parameter is older than 10 days. Any tweet older than 7 days will not be retrieved.")
        since = None

    id_since = find_id(api, since, query)
    id_until = find_id(api, until, query)

    print('Dates validated!\nFinding date ranges. This may take a while...')

    if since != None:
        id_since = find_id(api, since, query)

    if id_until != None and id_since != None:
        print ('Found date ranges!')
        return (id_since, id_until)
    else:
        print("Could not any Tweets within the date range. Please review your query.")
        sys.exit(0)


def date_check(since, until):
    now = datetime.datetime.utcnow()

    if since > until:
        print ("'since' parameter cannot be newer than 'until'.\nQuitting...")
        sys.exit(0)
    elif until < (now - datetime.timedelta(days = 8)):
        print ("'until' parameter cannot be older than 7 days as per Twitter API regulations.\nQuitting...")
        sys.exit(0)



def main():
    args = add_args()

    id_until = int(args.until)
    id_since = int(args.since)

    #date_check(date_since, date_until)

    manager = TokenManager()
    api = manager.init_api()

    #(id_since, id_until) = date_adjust(api, date_since, date_until, args.query)

    if args.outfile == None:
        args.outfile = args.query.split()[0] + '.csv'
    gather(api, args.query, id_since, id_until, args.outfile, args.maxtweets, args.toptweets)

if __name__== "__main__":
    main()
