FROM apache/airflow:2.8.3-python3.11

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jdk-headless curl && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java

COPY --chown=airflow:root start.sh /start.sh
RUN chmod +x /start.sh

# dbt-duckdb em venv isolado — criado como root, executável pelo airflow
# Separa completamente as dependencias do dbt das do Airflow/pyspark
RUN python -m venv /opt/dbt-venv && \
    PIP_USER=0 /opt/dbt-venv/bin/pip install --no-cache-dir dbt-duckdb==1.8.4

# A imagem do Airflow bloqueia pip como root — todos os pacotes do usuario
# devem ser instalados como USER airflow
USER airflow

COPY --chown=airflow:root requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# JAR do Iceberg: instalado no diretorio jars do pyspark (ja disponivel no PATH do airflow)
RUN PYSPARK_JARS=$(python -c 'import pyspark, os; print(os.path.join(os.path.dirname(pyspark.__file__), "jars"))') && \
    curl -fL \
    "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.5.0/iceberg-spark-runtime-3.5_2.12-1.5.0.jar" \
    -o "$PYSPARK_JARS/iceberg-spark-runtime-3.5_2.12-1.5.0.jar"

COPY --chown=airflow:root make_spark_conf.py /tmp/make_spark_conf.py
RUN python /tmp/make_spark_conf.py

# Garante que o diretório do DuckDB existe com ownership do airflow.
# Sem isso, o Docker inicializa o named volume como root e bloqueia escrita.
RUN mkdir -p /opt/airflow/dbt_db
