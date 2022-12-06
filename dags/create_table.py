from airflow.operators.python import PythonOperator
from airflow import DAG
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, timedelta
import pandas as pd


host = 'maslabase.c5ahny2xlnzd.us-east-1.rds.amazonaws.com'
user = 'lospibes'
passwd = 'scaloneta123'
db_name = 'maslabase'

credentials = {'consumer_key': "aiwD3XSHIHBfCeohJSvRU7kpw",
'consumer_secret' : "jVyQ4OpqAWr2EnNdqHWYKhvqqaaoJiZOV2WqNw5ZlIioJftGgJ",
'access_token' : "1545748698965200902-aHhEz4NIqhjAsNHcC4ORvVg6bMTdiH",
'access_token_secret' : "oBF6mPb9E95W6QXSXDKD2yyM0qsBJ7xrm5LRQmGLtid0m"}

#insert Database Name
DB_NAME = 'tweets_original'

#Me conecto
cnx = mysql.connector.connect(
        host = host,
        user = user,
        password = passwd)

cursor = cnx.cursor()

#creates db (Do Only Once)
def _create_database(cursor, database):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(database))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

def dag_create_database():
    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            _create_database(cursor, DB_NAME)
            print("Database {} created successfully.".format(DB_NAME))
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)

default_args = {"owner": "lospi", "retries": 0, "retry_delay": timedelta(minutes=0)}
with DAG(
    dag_id="create_database",
    default_args=default_args,
    start_date=datetime(2022, 12, 6),
    schedule_interval="0 10 * * *",
) as dag:
    create_database = PythonOperator(
        task_id="dag_create_database",
        python_callable=dag_create_database,
    )