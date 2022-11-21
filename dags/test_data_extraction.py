import pytest
from airflow.operators.python import PythonOperator
from datetime import datetime
import json

from dag_insert_daily_stock import _get_stock_data, STOCKS


@pytest.mark.parametrize("symbol", list(STOCKS.values()))
def test_data_extraction(symbol):
    task = PythonOperator(
        task_id="test",
        python_callable=_get_stock_data,
        op_args=[symbol],
    )
    result = task.execute(context={"ds": datetime.now().date().strftime("%Y-%m-%d")})

    assert type(result) == str

    result = json.loads(result)
    for column in ["date", "symbol", "open", "high", "low", "close", "volume"]:
        assert column in list(result.keys()), f"{column} not in data extraction"
