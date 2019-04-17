#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import tweepy
import json

class TokenManager:
    def write_config_json(self, api_key, api_secret, access_token, access_token_secret):
        cfg_dict = {}
        cfg_dict['api_key'] = api_key
        cfg_dict['api_secret'] = api_secret
        cfg_dict['access_token'] = access_token
        cfg_dict['access_token_secret'] = access_token_secret

        json_str = json.dumps(cfg_dict, indent=4)

        if not os.path.exists('config'):
            os.makedirs('config')

        with open('config/config.json', 'w') as f:
            f.write(json_str)



    def test_api(self, api_key, api_secret, access_token, access_token_secret):
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, retry_count=3, retry_delay=5, timeout=100, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        try:
            api.home_timeline()
            print ('\nAPI credentials validated...!')
            if not os.path.isfile('config.json'):
                self.write_config_json(api_key, api_secret, access_token, access_token_secret)
            return api

        except tweepy.error.TweepError as tweeperror:
            if tweeperror.message[0]['code'] == '89':
                print('\nInvalid or expired token. Please verify your credentials and try again\n')
            elif tweeperror.message[0]['code'] == '420':
                print('\nYou are currently rate-limited. Please wait 15 minutes and try again.\n')
            else:
                raise
            sys.exit(0)


    def first_cfg_api(self):
        print('Looks like you have not configured your API credentials yet. See https://developer.twitter.com/ for details\n')
        api_key = input('Please enter your API key:\n')
        api_secret = input('Please enter your API secret key:\n')
        access_token = input('Please enter your access token:\n')
        access_token_secret = input('Please enter your access token secret:\n')

        return self.test_api(api_key, api_secret, access_token, access_token_secret)


    def init_api(self):
        try:
            with open('config/config.json') as f:
                token = json.load(f)
            api = self.test_api(token['api_key'], token['api_secret'], token['access_token'], token['access_token_secret'])
            return api
        except IOError:
            api = self.first_cfg_api()
            return api
