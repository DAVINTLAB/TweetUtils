#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tweepy
import json
import argparse
import os
import sys

sys.path.append("..")

from modules.manager import TokenManager
#from ..modules.manager import TokenManager

def add_args():
    parser = argparse.ArgumentParser(description='Collects real-time streaming data from Twitter. Finalize the program with control-c')
    parser.add_argument('-k', '--keywords', metavar='', nargs='+', required=True, help='Keywords to perform the live search from. Keywords are separated by blank space. Takes one or more arguments.')
    parser.add_argument('-p', '--print', action="store_true", help='Print the contents of the tweets collected in real time')
    parser.add_argument('-o', '--outfile', metavar='', default='streaming_output.json', help='Filename for the resulting output. Default is "streaming_output.json"')
    return parser.parse_args()

class StdOutListener(tweepy.StreamListener):
    """ Class example taken from https://github.com/tweepy/tweepy/blob/master/examples/streaming.py
    """

    @staticmethod
    def json_format(data_json):
        current_tweet = {}
        current_tweet['id'] = data_json['id']
        current_tweet['created_at'] = data_json['created_at']
        current_tweet['username'] = data_json['user']['name']
        try:
            current_tweet['media_type'] = data_json['entities']['media'][0]['type']
            current_tweet['has_media'] = 'True'
        except:
            current_tweet['has_media'] = 'False'
            current_tweet['media_type'] = 'None'
        current_tweet['screen_name'] = data_json['user']['screen_name']
        current_tweet['retweet_count'] = data_json['retweet_count']
        current_tweet['favorite_count'] = data_json['favorite_count']
        current_tweet['text'] = data_json['text']
        current_tweet['lang'] = data_json['lang']
        return current_tweet

    def handle_interrupt(self):
        self.f.flush()
        sys.stdout.flush()
        print ('\nFinishing...')
        #dirty workaround
        self.f.seek(0, os.SEEK_END)
        self.f.seek(self.f.tell() - 2, os.SEEK_SET)
        self.f.write('\n]')

        print ('All done. File written to ' + self.outfile + '\n')
        sys.exit(0)

    def on_data(self, data):
        data_json = json.loads(data)
        current_tweet = self.json_format(data_json)
        self.f.write(json.dumps(current_tweet, ensure_ascii=False))
        self.f.write(',\n')
        self.counter+=1

        if self.prt:
            print(data_json['user']['name'])
            print (data_json['user']['screen_name'])
            print (data_json['text'])
            print ('\n')
        else:
            if sys.stdout.isatty():
                print("\rNumber of tweets collected so far...: %i"%self.counter, end='', flush=True)
            else:
                print(counter, end=' ', flush=True)

        return True


    def on_error(self, status):
        print(status)

    def __init__(self, outfile, prt):
        self.outfile = outfile
        self.f = open(outfile, 'w', encoding='utf8')
        self.f.write('[\n')
        self.prt = prt
        self.counter = 0

def main():
    args = add_args()
    l = StdOutListener(args.outfile, args.print)
    manager = TokenManager()
    api = manager.init_api()

    stream = tweepy.Stream(api.auth, l)
    try:
        stream.filter(track=args.keywords)
    except KeyboardInterrupt:
        l.handle_interrupt()

if __name__ == '__main__':
    main()
