import pandas as pd
# import config   # No lo ta leyendo
#SQL
import mysql.connector
from mysql.connector import errorcode
from sqlalchemy import create_engine
from airflow.operators.python import PythonOperator
from airflow import DAG

from datetime import datetime, timedelta

#from credentials_v2 import *
import tweepy
import datetime as dt
print(tweepy.__version__)

host = 'maslabase.c5ahny2xlnzd.us-east-1.rds.amazonaws.com'
user = 'lospibes'
passwd = 'scaloneta123'
db_name = 'tweets_original'

credentials = {'consumer_key': "aiwD3XSHIHBfCeohJSvRU7kpw",
'consumer_secret' : "jVyQ4OpqAWr2EnNdqHWYKhvqqaaoJiZOV2WqNw5ZlIioJftGgJ",
'access_token' : "1545748698965200902-aHhEz4NIqhjAsNHcC4ORvVg6bMTdiH",
'access_token_secret' : "oBF6mPb9E95W6QXSXDKD2yyM0qsBJ7xrm5LRQmGLtid0m"}


userID = 'CarlosMaslaton'
from_date = (datetime.now() + timedelta(days=-1)).date().strftime('%Y-%m-%d')

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

def dag_tweet_downloader(**context):
    # Authorize our Twitter credentials
    auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
    auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])
    api = tweepy.API(auth)

    alltweets = tweet_downloader(userID, from_date, credentials)

    # usar id, created_at, text
    df_tweets = pd.DataFrame()
    for i in range(len(alltweets)):
        tweet_dict = {'Id': [alltweets[i].id], 'Created_On':[alltweets[i].created_at.strftime("%m/%d/%Y, %H:%M:%S")], 'text': [alltweets[i].text]}
        df_tweets = df_tweets.append(pd.DataFrame(tweet_dict))

    df_tweets.reset_index(inplace=True)

    return df_tweets.to_json()

def insert_tweet(**context):
    task_instance = context["ti"]
    df_tweets = pd.read_json(
        task_instance.xcom_pull(task_ids='dag_tweet_downloader'),
        orient="index",
    ).T
    print(df_tweets)
    print(df_tweets.columns)
    df_tweets = df_tweets[['index', 'Id', 'Created_On', 'text']]
    # Appending Data to database:
    engine = create_engine(
        "mysql+mysqlconnector://{user}:{pwd}@{host}/{db}".format(user=user, pwd=passwd, host=host, db=db_name))
    df_tweets.to_sql(db_name, con=engine, if_exists='append')

default_args = {"owner": "lospi", "retries": 0, "retry_delay": timedelta(minutes=0)}
with DAG(
    dag_id="insert_daily_tweet",
    default_args=default_args,
    start_date=datetime(2022, 12, 6),
    schedule_interval="0 10 * * *",
) as dag:

    dag_tweet_downloader = PythonOperator(
        task_id="dag_tweet_downloader",
        python_callable=dag_tweet_downloader,
    )

    insert_tweet = PythonOperator(
        task_id="insert_tweet",
        python_callable=insert_tweet
    )

    dag_tweet_downloader >> insert_tweet