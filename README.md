# Local Docker Airflow + Spark + dbt Environment

Este projeto cria um ambiente local para:
- orquestração com Apache Airflow
- processamento PySpark com Iceberg
- transformação e testes com dbt

## Estrutura
- `docker-compose.yml` - define o Airflow e o Spark master
- `airflow/dags/etl_dag.py` - DAG que lê CSV, carrega Iceberg e executa dbt
- `spark/load_csv_to_iceberg.py` - job PySpark para criar a tabela Iceberg
- `dbt/` - projeto dbt com modelos e perfil Spark
- `data/` - CSV de entrada
- `warehouse/` - diretório local de dados Iceberg

## Como usar
1. No Windows, abra o Docker Desktop e habilite a integração WSL para Ubuntu 26.04.
2. No terminal WSL, entre na pasta do projeto:
   ```bash
   cd /home/raiaris/testelocaliza
   ```
3. Instale o Docker Compose plugin no WSL, se ainda não tiver:
   ```bash
   sudo apt update
   sudo apt install -y docker-compose-plugin
   ```
4. Suba o ambiente:
   ```bash
   docker compose up -d --build
   ```
5. Acesse o Airflow em:
   ```
   http://localhost:8080
   ```
5. Execute a DAG `pyspark_iceberg_dbt_pipeline` no UI do Airflow.

## Comandos úteis
- Ver serviços em execução:
  ```bash
  docker compose ps
  ```
- Ver logs do Airflow:
  ```bash
  docker compose logs -f airflow
  ```
- Executar dbt manualmente:
  ```bash
  docker compose exec airflow bash -lc 'cd /opt/airflow/dbt && dbt run --profiles-dir /opt/airflow/dbt'
  ```

## Observações
- O Spark grava o catálogo Iceberg em `./warehouse`.
- O DAG usa `spark-submit` e `dbt` do mesmo container Airflow.
- Se precisar ajustar colunas ou transformações, edite os arquivos em `dbt/models/`.
