# TweetUtils

  [![](https://img.shields.io/badge/python-3.4+-blue.svg)](https://www.python.org/download/releases/3.4.0/)

TweetUtils is a set of modules and command-line utilities for dealing with common-use cases for tweet datasets, as well as data collection from Twitter. A [Twitter Developer Account](https://developer.twitter.com/) is required for the data collection functionalities.

### Scripts

  - `streaming_gathering.py:` Gather real-time streaming data from Twitter with keyword filters
  - `search_gathering.py: ` Gather a  collection of tweets matching a specific [Twitter query](https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html)
  - `profile_gathering.py: ` Gather a collection of tweets from a specific user profile
  - `sanitize_tweets.py:` Remove stopwords, emoji and other customizable options
  - `quick_report.py:` Prints out a summary of contents for a dataset, such as top tweets, date range, most tweeted words, hashtags, tag cloud sizes...

### Modules

Additionally, you may opt to use the modules as a programming interface.

  - `token_manager.py:` Handles OAuth authentication within the Twitter API using [Tweepy](http://www.tweepy.org/)
  - `sanitizer.py: ` Stores all text-cleaning functions, such as stopword removal, symbol removal, emoji removal...
  - `io.py:` Reads and writes JSON and CSV files in a streamlined way

### Installation

Install the dependencies and run the scripts/import the modules.

```sh
$ cd TweetUtils
$ pip install -r requirements.txt
```
