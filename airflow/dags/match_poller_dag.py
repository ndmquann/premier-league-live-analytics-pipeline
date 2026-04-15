from airflow import DAG
from airflow.operators.python import ShortCircuitOperator, PythonOperator
from datetime import datetime, timedelta
from app.fetchers.scores import get_live_scores, extract_match_info, is_match_live
from app.fetchers.fixtures import get_today_fixtures

with DAG(
    dag_id="match_poller_dag",
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=1),
        "email_on_failure": True,
        "email": "minhquan.nguyendo.0705@gmail.com"
    },
    start_date=datetime(2024, 1, 1),
    schedule="*/15 * * * *", # Run every 15 minutes
    catchup=False
) as dag:
    
    def check_live():
        matches = get_today_fixtures()
        return is_match_live(matches)
    
    def fetch_scores_task():
        matches = get_live_scores()
        return matches

    def match_info_task(**context):
        ti = context["ti"]
        matches = ti.xcom_pull(task_ids="fetch_scores") # store return data
        result = []
        for match in matches["matches"]:
            result.append(extract_match_info(match))
        return result
     
    fetch_lives = ShortCircuitOperator(
        task_id="fetch_lives",
        python_callable=check_live
    )

    fetch_scores = PythonOperator(
        task_id="fetch_scores",
        python_callable=fetch_scores_task
    )

    fetch_goals = PythonOperator(
        task_id="fetch_goals",
        python_callable=match_info_task
    )

    fetch_lives >> fetch_scores >> fetch_goals