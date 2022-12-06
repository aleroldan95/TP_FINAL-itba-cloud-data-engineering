from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow import DAG
from datetime import datetime, timedelta

default_args = {"owner": "ale", "retries": 5, "retry_delay": timedelta(minutes=5)}

with DAG(
    dag_id="dag_with_postgres_operator_v1",
    default_args=default_args,
    start_date=datetime(2022, 10, 6),
    schedule_interval="0 0 * * *",
) as dag:
    task1 = PostgresOperator(
        task_id="create_postgres_table",
        postgres_conn_id="postgres_localhost",
        sql="""
            create table if not exists dags_run (
                dt date,
                dag_id character varying,
                primary key (dt, dag_id)
            )
        """,
    )
    task1
