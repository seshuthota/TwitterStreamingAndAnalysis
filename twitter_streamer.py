import re
import matplotlib.pyplot as plt
import pandas as pd
from textblob import TextBlob
from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

import twitter_credentials


# Twitter Client
class TwitterClient():

    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator.authenticate_twitter_app(self)
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(home_timeline_tweets)
        return home_timeline_tweets


# Twitter Authenticator
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth


# Twitter streamer
class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles twitter authentication and connection to the twitter stream API.

        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth=auth, listener=listener)
        stream.filter(track=hash_tag_list)


# Twitter stream listener
class TwitterListener(StreamListener):
    """
    This is a basic listener class that prints received tweets to the standard output.
    """

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, raw_data):
        try:
            print(raw_data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(raw_data)
            return True
        except BaseException as e:
            print("Error on data %s" % str(e))
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # Returning false on_data method in case if rate limit occurs.
            print("Error with status 420")
            return False
        print(status_code)


class TweetAnalyzer:
    """
    Functionality for analyzing and categorizing tweets
    """

    @staticmethod
    def clean_tweet(tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_data_frame(self, tweets):
        cols = ["Tweets", "id", "len", "date", "source", "likes", "retweets", "sentiment"]
        lst = []
        for tweet in tweets:
            lst.append([tweet.text, tweet.id, len(tweet.text), tweet.created_at, tweet.source, tweet.favorite_count,
                        tweet.retweet_count, self.analyze_sentiment(tweet.text)])
        df = pd.DataFrame(lst, columns=cols)
        df["date"] = pd.to_datetime(df["date"])
        return df


if __name__ == "__main__":
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    tweets = api.user_timeline(screen_name="elonmusk", count=2000)
    tweet_analyzer = TweetAnalyzer()
    data = tweet_analyzer.tweets_to_data_frame(tweets)

    tweet_likes = pd.Series(data["likes"].values, index=data["date"])
    tweet_likes.plot(figsize=(16, 4), color='r', legend=True)

    tweet_retweets = pd.Series(data["retweets"].values, index=data["date"])
    tweet_retweets.plot(figsize=(16, 4), color='b', legend=True)
    plt.show()
    print(data.head())
