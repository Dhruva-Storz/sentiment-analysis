from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor

from textblob import TextBlob
import re

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import twittercredentials


class TwitterClient():
	def __init__(self, twitter_user=None):
		self.auth = TwitterAuthenticator().authenticate_twitter_app()
		self.twitter_client = API(self.auth)

		self.twitter_user = twitter_user

	def get_twitter_client_api(self):
		return self.twitter_client

	def get_user_timeline_tweets(self, num_tweets):
		tweets = []
		for tweet in Cursor(self.twitter_client.user_timeline, id = self.twitter_user).items(num_tweets):
			tweets.append(tweet)

		return tweets

	def get_friend_list(self, num_friends):
		friend_list = []
		for friend in Cursor(self.twitter_client.friends).items(num_friends):
			friend_list.append(friend)
		return friend_list

	def get_home_timeline_tweets(self, num_tweets):
		tweets = []
		for tweet in Cursor(self.twitter_client.home_timeline).items(num_tweets):
			tweets.append(tweet)
		return tweets


class TwitterAuthenticator():

	def authenticate_twitter_app(self):
		auth = OAuthHandler(twittercredentials.CONSUMER_KEY, twittercredentials.CONSUMER_SECRET)
		auth.set_access_token(twittercredentials.ACCESS_TOKEN, twittercredentials.ACCESS_TOKEN_SECRET)
		return auth

class TwitterStreamer():
	"""
	Class for streaming and processing live tweets.
	"""
	def __init__(self):
		self.twitter_authenticator = TwitterAuthenticator()

	def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
		listener = TwitterListener(fetched_tweets_filename)
		auth = self.twitter_authenticator.authenticate_twitter_app()
		stream = Stream(auth, listener)

		stream.filter(track = hash_tag_list)
	
class TwitterListener(StreamListener):
	"""
	Basic listener class
	"""
	def __init__(self, fetched_tweets_filename):
		self.fetched_tweets_filename = fetched_tweets_filename 

	def on_data(self,data):
		try:
			print(data)
			with open(self.fetched_tweets_filename, 'a') as tf:
				tf.write(data)
			print(data)
		except BaseException as e:
			print("Error")
		return True
	
	def on_error(self, status):
		if status == 420:
			# in case rate limit occurs (can get kicked indefinitely if ignored forever)
			return False
		print(str(status))

class TweetAnalyzer():
	"""
	analysing and categorizing tweet content
	"""

	def clean_tweet(self, tweet):
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

	def analyse_sentiment(self, tweet):
		cleaned = self.clean_tweet(tweet)
		analysis = TextBlob(cleaned)

		if analysis.sentiment.polarity > 0:
			return 1
		elif analysis.sentiment.polarity == 0:
			return 0
		else:
			return -1

	def tweets_to_data_frame(self, tweets):
		df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=["tweets"])
		df['id'] = np.array([tweet.id for tweet in tweets])
		df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
		df['source'] = np.array([tweet.source for tweet in tweets])
		df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
		df['length'] = np.array([len(tweet.text) for tweet in tweets])
		df['date'] = np.array([tweet.created_at for tweet in tweets])
		df['polarity'] = np.array([self.analyse_sentiment(tweet.text) for tweet in tweets])
		return df

if __name__=="__main__":

	twitter_client = TwitterClient()
	api = twitter_client.get_twitter_client_api()

	tweets = api.user_timeline(screen_name="dog_feelings", count=200)

	tweet_analyser = TweetAnalyzer()
	df = tweet_analyser.tweets_to_data_frame(tweets)
	print(df.head(10))
	#
	# # average length of tweets
	# print(np.mean(df['length']))
	#
	# # number of likes for most liked tweet
	# print(np.max(df['likes']))

	#Time Series
	time_likes = pd.Series(data=df['polarity'].values, index=df['date'])
	time_likes.plot(figsize=(16,4), color = 'b')
	#time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
	#time_retweets.plot(figsize=(16, 4), label="retweets", legend=True)
	plt.show()

	# print(tweets[0].retweet_count)

	# hash_list = ['donald trump','hillary clinton', 'barack obama', 'bernie sanders']
	# fetched_tweets_filename = "tweets.json"
	# twitter_streamer = TwitterStreamer()
	# twitter_streamer.stream_tweets(fetched_tweets_filename, hash_list)
	#
	# twitter_client = TwitterClient('pycon')
	# for tweet in twitter_client.get_home_timeline_tweets(5):
	# 	print(tweet)