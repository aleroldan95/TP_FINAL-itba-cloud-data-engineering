from airflow.operators.python import PythonOperator
from airflow import DAG
from datetime import datetime, timedelta
import pandas as pd
from time import sleep

# import plotly.express as px

from postgres import Postgres
import requests
import json
import numpy as np
import sqlalchemy.exc


default_args = {"owner": "ale", "retries": 0, "retry_delay": timedelta(minutes=0)}

URL = "https://www.alphavantage.co/query"
FUNCTION = "TIME_SERIES_DAILY"
API_KEY = "TFHNYCWBD71JBSON"
STOCKS = {"google": "GOOG", "microsoft": "MSFT", "amazon": "AMZN"}
SQL_STOCK_DATA = "stock_value"


def _get_stock_data(stock_symbol, **context):
    # Run one day ago
    date = (datetime.strptime(context["ds"], "%Y-%m-%d") - timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )

    entrypoint = f"{URL}?function={FUNCTION}&symbol={stock_symbol}&apikey={API_KEY}&datatype=json"
    r = requests.get(entrypoint)
    sleep(10)  # To avoid api limits
    data = json.loads(r.content)

    df = (
        pd.DataFrame(data["Time Series (Daily)"])
        .T.reset_index()
        .rename(columns={"index": "date"})
    )
    df = df[df["date"] == date]

    if not df.empty:
        df_final = pd.DataFrame(
            {
                "date": [date],
                "symbol": [stock_symbol],
                "open": [float(df["1. open"].values[0])],
                "high": [float(df["2. high"].values[0])],
                "low": [float(df["3. low"].values[0])],
                "close": [float(df["4. close"].values[0])],
                "volume": [float(df["5. volume"].values[0])],
            }
        )
    else:
        df_final = pd.DataFrame(
            [[date, stock_symbol, np.nan, np.nan, np.nan, np.nan, np.nan]],
            columns=["date", "symbol", "open", "high", "low", "close", "volume"],
        )

    return df_final.to_json()


def _insert_daily_stock(**context):
    task_instance = context["ti"]
    dfs = []
    for ticker in STOCKS:
        stock_df = pd.read_json(
            task_instance.xcom_pull(task_ids=f"get_daily_data_{ticker}"),
            orient="index",
        ).T
        stock_df = stock_df[
            ["date", "symbol", "open", "high", "low", "close", "volume"]
        ]
        dfs.append(stock_df)
    df = pd.concat(dfs, axis=0)
    print(df)
    postgres = Postgres("postgres_localhost")
    try:
        postgres.insert_from_frame(
            df=df, table=SQL_STOCK_DATA, if_exists="append", index=False
        )
        print(f"Inserted {len(df)} records")
    except sqlalchemy.exc.IntegrityError:
        # You can avoid doing this by setting a trigger rule in the reports operator
        print("Data already exists! Nothing to do...")


def _generate_report(**context):
    initial_date = (
        datetime.strptime(context["ds"], "%Y-%m-%d") - timedelta(days=8)
    ).strftime("%Y-%m-%d")
    final_date = (
        datetime.strptime(context["ds"], "%Y-%m-%d") - timedelta(days=1)
    ).strftime("%Y-%m-%d")

    postgres = Postgres("postgres_localhost")
    query = f"""
        SELECT 
        * 
        FROM stock_value
        where 1=1
            and date between '{initial_date}' and '{final_date}'
            and symbol in ({str(list(STOCKS.values())).replace('[','').replace(']','')})
        """
    df = postgres.to_frame(query)
    import seaborn as sns

    sns.lineplot(df, x="date", y="close", hue="symbol")

    return df.to_json()
    # fig = px.line(df, x="date", y="close", color='symbol')
    # fig.show()
    # print(fig)


with DAG(
    dag_id="insert_daily_stock",
    default_args=default_args,
    start_date=datetime(2022, 10, 6),
    schedule_interval="0 10 * * *",
) as dag:
    get_stock_data = {}
    for company, symbol in STOCKS.items():
        get_stock_data[company] = PythonOperator(
            task_id=f"get_daily_data_{company}",
            python_callable=_get_stock_data,
            op_args=[symbol],
        )

    insert_daily_stock = PythonOperator(
        task_id="insert_daily_stock",
        python_callable=_insert_daily_stock,
    )

    generate_report = PythonOperator(
        task_id="generate_report", python_callable=_generate_report
    )

    for company in STOCKS:
        task = get_stock_data[company]
        task.set_downstream(insert_daily_stock)
    insert_daily_stock.set_downstream(generate_report)
