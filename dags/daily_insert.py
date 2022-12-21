import pandas as pd
from airflow.operators.python import PythonOperator
from airflow import DAG
from airflow.models import Variable
from postgres import Postgres
import sqlalchemy.exc
from sentiment_analysis_spanish import sentiment_analysis
import json
import boto3

from datetime import datetime, timedelta

#from credentials_v2 import *
import tweepy
import datetime as dt
print(tweepy.__version__)


userID = 'CarlosMaslaton'

SQL_TABLE='masla_tweets'

def tweet_downloader(userID, from_date):
    print(f'Download prints from: {from_date}')
    # Authorize our Twitter credentials
    credentials = json.loads(Variable.get("credentials"))

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

    filtered = []

    for i in alltweets:
        if i.created_at > since_date:
            filtered.append(i)

    print(f'Downloaded {len(filtered)} tweets')

    return filtered


def dag_tweet_downloader(**context):
    from_date = (datetime.strptime(context["ds"], "%Y-%m-%d") - timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )
    # Authorize our Twitter credentials
    credentials = json.loads(Variable.get("credentials"))
    auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
    auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])
    api = tweepy.API(auth)

    alltweets = tweet_downloader(userID, from_date)

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
    df_tweets.rename(columns={"Created_On": "date", "Id": "id"}, inplace=True)
    df_tweets = df_tweets[['id', 'date', 'text']]
    # Appending Data to database:
    postgres = Postgres("postgres_maslabot")
    try:
        postgres.insert_from_frame(
            df=df_tweets, table=SQL_TABLE, if_exists="append", index=False
        )
        print(f"Inserted {len(df_tweets)} records")
    except sqlalchemy.exc.IntegrityError:
        print("Data already exists! Nothing to do...")

    #engine = create_engine(
    #    "mysql+mysqlconnector://{user}:{pwd}@{host}/{db}".format(user=user, pwd=passwd, host=host, db=db_name))
    #df_tweets.to_sql(db_name, con=engine, if_exists='append')

def insert_sentiment(**context):
    task_instance = context["ti"]
    df_tweets = pd.read_json(
        task_instance.xcom_pull(task_ids='dag_tweet_downloader'),
        orient="index",
    ).T
    df_tweets.rename(columns={"Created_On": "date", "Id": "id"}, inplace=True)
    df_tweets = df_tweets[['id', 'text']]
    #Adding Sentiment
    sentiment = sentiment_analysis.SentimentAnalysisSpanish()
    sentiment_column = []
    for index, row in df_tweets.iterrows():
        sentiment_column.append(sentiment.sentiment(row['text']))
    df_tweets['sentiment'] = sentiment_column
    df_tweets = df_tweets[['id', 'sentiment']]
    # Appending Data to database:
    postgres = Postgres("postgres_maslabot")
    try:
        postgres.insert_from_frame(
            df=df_tweets, table='masla_sentiment', if_exists="append", index=False
        )
        print(f"Inserted {len(df_tweets)} records")
    except sqlalchemy.exc.IntegrityError:
        print("Data already exists! Nothing to do...")

    median_sentiment = str(df_tweets['sentiment'].astype('float').median())

    return median_sentiment

def sentiment_tweet(**context):
    median_sentiment = context["ti"].xcom_pull(task_ids='insert_sentiment')
    aws_details = json.loads(Variable.get("aws_details"))
    s3_client = boto3.client('s3'
                             , aws_access_key_id=aws_details["aws_access_key_id"]
                             , aws_secret_access_key=aws_details["aws_secret_access_key"],
                             aws_session_token=aws_details["aws_session_token"])

    if float(median_sentiment)>0.2:
        s3_client.download_file("maslaton-moods", "bullish.jpeg", "/tmp/bullish.png")
        imagePath = "/tmp/bullish.png"
        status = f"""Masla status: bullish ({median_sentiment})"""
    else:
        s3_client.download_file("maslaton-moods", "bearish.jpeg", "/tmp/bearish.png")
        imagePath = "/tmp/bearish.png"
        status = f"""Masla status: bearish ({median_sentiment})"""

    credentials = json.loads(Variable.get("credentials"))
    auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
    auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])
    api = tweepy.API(auth)
    api.update_status_with_media(status=status, filename=imagePath)

default_args = {"owner": "lospi", "retries": 0, "retry_delay": timedelta(minutes=0)}
with DAG(
    dag_id="insert_daily_tweet",
    default_args=default_args,
    start_date=datetime(2022, 12, 17),
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

    insert_sentiment = PythonOperator(
        task_id="insert_sentiment",
        python_callable=insert_sentiment
    )

    sentiment_tweet = PythonOperator(
        task_id="sentiment_tweet",
        python_callable=sentiment_tweet
    )

    dag_tweet_downloader >> insert_tweet >> insert_sentiment >> sentiment_tweet