from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from app.fetchers.fixtures import get_today_fixtures
from app.fetchers.standings import get_standings
from app.fetchers.liverpool import get_liverpool_last_results
from app.db.database import save_teams, save_standings, save_matches

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
    
    def _get_fixtures():
        data = get_today_fixtures()
        return data
    
    def _get_standings():
        data = get_standings()
        return data

    def _save_teams(**context):
        ti = context["ti"]
        table = ti.xcom_pull(task_ids="fetch_standings")
        teams = []
        for team in table:
            teams.append(team["team"])
        save_teams(teams)
    
    def _save_standings(**context):
        ti = context["ti"]
        table = ti.xcom_pull(task_ids="fetch_standings")
        save_standings(table)
    
    def _save_matches(**context):
        ti = context["ti"]
        matches = ti.xcom_pull(task_ids="fetch_fixtures")
        save_matches(matches)

    fetch_fixtures = PythonOperator(
        task_id="fetch_fixtures",
        python_callable=_get_fixtures
    )

    save_teams_task = PythonOperator(
        task_id="save_teams",
        python_callable=_save_teams
    )

    save_matches_task = PythonOperator(
        task_id="save_matches",
        python_callable=_save_matches
    )

    fetch_standings = PythonOperator(
        task_id="fetch_standings",
        python_callable=_get_standings
    )

    save_standings_task = PythonOperator(
        task_id="save_standings",
        python_callable=_save_standings
    )

    fetch_liverpool = PythonOperator(
        task_id="fetch_liverpool",
        python_callable=get_liverpool_last_results
    )

    fetch_fixtures >> fetch_standings >> save_teams_task >> save_standings_task >> save_matches_task >> fetch_liverpool