from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="vortex_dbt_example",
    description="Run dbt transformations for the Vortex example pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 * * * *",
    catchup=False,
    max_active_runs=1,
    tags=["vortex", "dbt", "example"],
) as dag:
    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "dbt run "
            "--project-dir /opt/vortex/dbt "
            "--profiles-dir /opt/vortex/dbt/profiles "
            "--target ${DBT_TARGET:-dev}"
        ),
        env={
            "DBT_TARGET": "dev",
            "DBT_POSTGRES_HOST": "postgres",
            "DBT_POSTGRES_PORT": "5432",
            "DBT_POSTGRES_DB": "vortex",
            "DBT_POSTGRES_USER": "postgres",
            "DBT_POSTGRES_PASSWORD": "postgres",
            "DBT_POSTGRES_SCHEMA": "analytics",
        },
    )

    run_dbt
