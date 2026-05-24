#!/bin/bash
set -e

# Runs as root — fix permissions on bind-mounted dirs so airflow user can write
mkdir -p /opt/airflow/dbt/edr_target
chmod -R 777 /opt/airflow/dbt/edr_target
mkdir -p /data/edr_report
chmod -R 777 /data/edr_report

# Drop to airflow user for all Airflow processes
exec su -s /bin/bash airflow -c '
  airflow db migrate

  airflow users create \
      --username admin \
      --password admin \
      --firstname Admin \
      --lastname User \
      --role Admin \
      --email admin@example.com || true

  airflow scheduler &
  exec airflow webserver
'
