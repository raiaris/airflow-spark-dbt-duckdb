from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="pyspark_iceberg_dbt_pipeline",
    start_date=datetime(2026, 5, 22),
    schedule_interval=None,
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["spark", "iceberg", "dbt"],
) as dag:

    load_csv = BashOperator(
        task_id="load_csv_to_iceberg",
        bash_command=(
            "spark-submit "
            "--master spark://spark-master:7077 "
            "--packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0 "
            "/opt/spark/load_csv_to_iceberg.py "
            "{{ ds }} "
            "\"{{ run_id }}\""
        ),
    )

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command="cd /opt/airflow/dbt && /opt/dbt-venv/bin/dbt deps --profiles-dir /opt/airflow/dbt",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && /opt/dbt-venv/bin/dbt run --profiles-dir /opt/airflow/dbt",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && /opt/dbt-venv/bin/dbt test --profiles-dir /opt/airflow/dbt",
    )

    dbt_docs_generate = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=(
            "cd /opt/airflow/dbt && "
            "/opt/dbt-venv/bin/dbt docs generate "
            "--profiles-dir /opt/airflow/dbt"
        ),
    )

    edr_report = BashOperator(
        task_id="edr_report",
        bash_command=(
            "mkdir -p /data/edr_report && "
            "cd /opt/airflow/dbt && "
            "/opt/dbt-venv/bin/edr report "
            "--profiles-dir /opt/airflow/dbt "
            "--project-dir /opt/airflow/dbt "
            "--file-path /data/edr_report/elementary_report.html"
        ),
    )

    load_csv >> dbt_deps >> dbt_run >> dbt_test >> dbt_docs_generate >> edr_report
