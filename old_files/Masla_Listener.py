from credentials_v2 import *
import tweepy
import datetime as dt
print(tweepy.__version__)


def tweet_downloader(userID, from_date, credentials):
    # Authorize our Twitter credentials
    auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
    auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])
    api = tweepy.API(auth)

    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=userID, count=200)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    since_date = dt.datetime.strptime(from_date, '%Y-%m-%d')
    since_date = since_date.replace(tzinfo=dt.timezone.utc)

    while alltweets[-1].created_at > since_date:
        # print("getting tweets before {}".format(oldest))

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=userID, count=200, max_id=oldest)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print("...{} tweets downloaded so far".format(len(alltweets)))

    return alltweets[:-1]

# Authorize our Twitter credentials
auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])
api = tweepy.API(auth)

alltweets = []

userID = 'CarlosMaslaton'
from_date = '2022-11-17'

alltweets = tweet_downloader(userID, from_date, credentials)

alltweets[-1].text