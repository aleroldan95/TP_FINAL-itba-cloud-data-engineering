from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow import DAG
from datetime import datetime, timedelta
from sqlalchemy.inspection import inspect
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.engine import Engine
from model_maslabot import Base

default_args = {"owner": "lospi", "retries": 0, "retry_delay": timedelta(minutes=0)}

def create_table_if_not_exists():
    pg_hook = PostgresHook(postgres_conn_id="postgres_maslabot")
    pg_engine: Engine = pg_hook.get_sqlalchemy_engine()
    pg_inspector: Inspector = inspect(pg_engine)
    table_names: [str] = pg_inspector.get_table_names(schema="maslabot")
    if "masla_tweets" not in table_names and "masla_sentiment" not in table_names :
        Base.metadata.create_all(pg_engine)
        print('New Tables Created')
    else:
        print('Tables already exits')


with DAG(
    dag_id="create_table_tweets_daily",
    default_args=default_args,
    start_date=datetime(2022, 12, 17),
    schedule_interval="@once",
) as dag:
    create_table_if_not_exists = PythonOperator(
        task_id="create_table_if_not_exists",
        python_callable=create_table_if_not_exists,
    )
    create_table_if_not_exists
