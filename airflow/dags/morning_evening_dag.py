from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from app.fetchers.fixtures import get_today_fixtures
from app.fetchers.standings import get_standings
from app.fetchers.liverpool import get_liverpool_last_results

with DAG(
    dag_id="morning_evening_dag",
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=1),
        "email_on_failure": True,
        "email": "minhquan.nguyendo.0705@gmail.com"
    },
    start_date=datetime(2024, 1, 1),
    schedule="0 8,18 * * *",
    catchup=False
) as dag:
    fetch_fixtures = PythonOperator(
        task_id="fetch_fixtures",
        python_callable=get_today_fixtures
    )

    fetch_standings = PythonOperator(
        task_id="fetch_standings",
        python_callable=get_standings
    )

    fetch_liverpool = PythonOperator(
        task_id="fetch_liverpool",
        python_callable=get_liverpool_last_results
    )

    fetch_fixtures >> fetch_standings >> fetch_liverpool