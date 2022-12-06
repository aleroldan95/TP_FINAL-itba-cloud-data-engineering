import pandas as pd
# import config   # No lo ta leyendo
#SQL
import mysql.connector
from mysql.connector import errorcode
from sqlalchemy import create_engine


#from credentials_v2 import *
import tweepy
import datetime as dt
print(tweepy.__version__)

host = 'maslabase.c5ahny2xlnzd.us-east-1.rds.amazonaws.com'
user = 'lospibes'
passwd = 'scaloneta123'
db_name = 'maslabase'

credentials = {'consumer_key': "aiwD3XSHIHBfCeohJSvRU7kpw",
'consumer_secret' : "jVyQ4OpqAWr2EnNdqHWYKhvqqaaoJiZOV2WqNw5ZlIioJftGgJ",
'access_token' : "1545748698965200902-aHhEz4NIqhjAsNHcC4ORvVg6bMTdiH",
'access_token_secret' : "oBF6mPb9E95W6QXSXDKD2yyM0qsBJ7xrm5LRQmGLtid0m"}


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
from_date = '2022-11-29'

alltweets = tweet_downloader(userID, from_date, credentials)

type(alltweets)  #list

# usar id, created_at, text
df_tweets = pd.DataFrame()
for i in range(len(alltweets)):
    tweet_dict = {'Id': [alltweets[i].id], 'Created_On':[alltweets[i].created_at.strftime("%m/%d/%Y, %H:%M:%S")], 'text': [alltweets[i].text]}
    df_tweets = df_tweets.append(pd.DataFrame(tweet_dict))

#Me conecto
cnx = mysql.connector.connect(
        host = host,
        user = user,
        password = passwd)
print(cnx)
cursor = cnx.cursor()

#insert Database Name
db_name = 'tweets_original'

#creates db (Do Only Once)

def create_database(cursor, database):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(database))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cursor.execute("USE {}".format(db_name))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(db_name))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor, db_name)
        print("Database {} created successfully.".format(db_name))
        cnx.database = db_name
    else:
        print(err)
        exit(1)


# Appending Data to database:
engine = create_engine("mysql+mysqlconnector://{user}:{pwd}@{host}/{db}".format(user=user, pwd = passwd, host= host, db = db_name))
df_tweets.to_sql(db_name, con = engine, if_exists = 'append')