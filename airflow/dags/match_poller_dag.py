from airflow import DAG
from airflow.operators.python import ShortCircuitOperator, PythonOperator
from datetime import datetime, timedelta
from app.fetchers.scores import get_live_scores, is_match_live
from app.fetchers.fixtures import get_today_fixtures

with DAG(
    dag_id="match_poller_dag",
    start_date=datetime(2024, 1, 1),
    schedule="*/15 * * * *", # Run every 15 minutes
    catchup=False
) as dag:
    
    def _check_live():
        matches = get_today_fixtures()
        return is_match_live(matches)
    
    def _fetch_scores_task():
        matches = get_live_scores()
        return matches
                
    fetch_lives = ShortCircuitOperator(
        task_id="fetch_lives",
        python_callable=_check_live
    )

    fetch_scores = PythonOperator(
        task_id="fetch_scores",
        python_callable=_fetch_scores_task
    )

    fetch_lives >> fetch_scores