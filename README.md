# Airflow + Spark + dbt + DuckDB — Pipeline Local

Pipeline de dados local para detecção de fraude em transações financeiras, com orquestração Airflow, ingestão PySpark/Iceberg, transformações dbt/DuckDB e monitoramento de qualidade com Elementary.

## Arquitetura da Solução

```mermaid
flowchart TD
    %% ─── FONTE ───
    CSV["📄 df_fraud_credit.csv\nDado bruto de fraudes em cartão"]

    %% ─── ORQUESTRAÇÃO ───
    subgraph AIRFLOW["🌀 Apache Airflow  •  :8080"]
        direction TB
        DAG["DAG: pyspark_iceberg_dbt_pipeline\nTrigger manual · SequentialExecutor"]
        T1["Task 1\nload_csv_to_iceberg"]
        T2["Task 2\ndbt deps"]
        T3["Task 3\ndbt run"]
        T4["Task 4\ndbt test"]
        T5["Task 5\ndbt docs generate"]
        T6["Task 6\nedr report"]
        DAG --> T1 --> T2 --> T3 --> T4 --> T5 --> T6
    end

    %% ─── INGESTÃO ───
    subgraph SPARK["⚡ Apache Spark 3.5  •  Standalone Cluster"]
        direction LR
        SM["spark-master\n:7077"]
        SW["spark-worker"]
        SCRIPT["load_csv_to_iceberg.py\nPySpark + Iceberg Runtime 1.5"]
        SM --- SW
        SCRIPT --> SM
    end

    subgraph ICEBERG["🗂️ Apache Iceberg"]
        ICE["Iceberg Table\nwarehouse/default/fraud_raw\nParquet particionado\nyear / month / day / dagrun_id"]
    end

    %% ─── TRANSFORMAÇÃO ───
    subgraph DBT["🔧 dbt-duckdb  •  /opt/dbt-venv"]
        direction TB
        SRC["Source\niceberg_warehouse.fraud_raw\n↳ iceberg_scan() via DuckDB extension"]
        STG["Staging\nstg_fraud__transactions\nCasts de tipo · filtros · enriquecimento"]
        M1["Mart\namount\nTop 3 maiores vendas\npor receiving_address"]
        M2["Mart\nrisk_score_average\nAvg risk score\npor location_region"]
        SRC --> STG --> M1
        STG --> M2
    end

    subgraph DQ["🔍 Qualidade de Dados  •  Elementary"]
        direction TB
        DET["Testes Determinísticos\nnot_null · accepted_values\n→ severity: warn"]
        STAT["Testes Estatísticos\nvolume_anomalies\nall_columns_anomalies\ncolumn_anomalies (amount · risk_score)"]
        DET -. acumula histórico .-> STAT
    end

    %% ─── PERSISTÊNCIA ───
    subgraph DUCKDB["🦆 DuckDB  •  fraud_warehouse.duckdb"]
        direction LR
        SMAIN["schema: main\nModelos dbt materializados"]
        SELEM["schema: main_elementary\nMetadados e histórico de qualidade"]
    end

    %% ─── SERVING ───
    subgraph SERVE["🌐 Camada de Visualização"]
        direction LR
        DOCS["dbt Docs\nnginx :8082\ndbt/target/"]
        REPORT["Elementary Report\nnginx :8083\ndata/edr_report/\nelementary_report.html"]
    end

    %% ─── INFRAESTRUTURA ───
    subgraph INFRA["🐳 Docker Compose  •  WSL2"]
        INIT["init service (busybox)\nchmod 777 em bind-mounts\n↳ garante permissões UID 50000"]
    end

    %% ─── CONEXÕES PRINCIPAIS ───
    CSV -->|lido por| T1
    T1 -->|spark-submit| SCRIPT
    SCRIPT -->|escreve Parquet| ICE
    T3 -->|executa| DBT
    ICE -->|iceberg_scan| SRC
    STG -->|testes rodados em| DQ
    M1 & M2 -->|materializa tabelas| SMAIN
    DQ -->|grava métricas| SELEM
    T5 -->|gera artefatos| DOCS
    T6 -->|gera HTML| REPORT
    INFRA -.->|provisiona| AIRFLOW & SPARK & DBT

    %% ─── ESTILOS ───
    classDef source fill:#f5a623,color:#000,stroke:#c47d0e
    classDef airflow fill:#017cee,color:#fff,stroke:#0056a3
    classDef spark fill:#e25a1c,color:#fff,stroke:#a03c10
    classDef iceberg fill:#3d9970,color:#fff,stroke:#2a6b4e
    classDef dbt fill:#ff694b,color:#fff,stroke:#c04030
    classDef dq fill:#9b59b6,color:#fff,stroke:#6c3483
    classDef duck fill:#f1c40f,color:#000,stroke:#b7950b
    classDef serve fill:#1abc9c,color:#fff,stroke:#148f77
    classDef infra fill:#7f8c8d,color:#fff,stroke:#555

    class CSV source
    class DAG,T1,T2,T3,T4,T5,T6 airflow
    class SM,SW,SCRIPT spark
    class ICE iceberg
    class SRC,STG,M1,M2 dbt
    class DET,STAT dq
    class SMAIN,SELEM duck
    class DOCS,REPORT serve
    class INIT infra
```

## Pré-requisitos

- Docker Desktop com integração WSL habilitada
- Docker Compose plugin instalado no WSL:
  ```bash
  sudo apt update && sudo apt install -y docker-compose-plugin
  ```
- Harlequin instalado no WSL (para consulta local ao DuckDB):
  ```bash
  pip install harlequin
  ```

## Iniciando do zero

```bash
# 1. Clone e entre na pasta
git clone <url-do-repo>
cd airflow-spark-dbt-duckdb

# 2. Suba todos os serviços (build incluso)
docker compose up -d --build

# 3. Aguarde o Airflow inicializar (~30s) e acesse
#    http://localhost:8080  (usuário: admin / senha: admin)

# 4. Ative e execute a DAG "pyspark_iceberg_dbt_pipeline" pelo UI do Airflow
```

O pipeline roda na seguinte ordem:

```
load_csv_to_iceberg → dbt_deps → dbt_run → dbt_test → dbt_docs_generate → edr_report
```

Após a conclusão, todos os dados estarão disponíveis no DuckDB e os relatórios acessíveis nas URLs abaixo.

## Interfaces disponíveis

| Interface | URL | Descrição |
|---|---|---|
| Airflow | http://localhost:8080 | Orquestração e logs de execução |
| dbt Docs | http://localhost:8082 | Lineage, descrições e testes dos modelos |
| Elementary | http://localhost:8083 | Relatório de qualidade de dados |

## Consultando os dados com Harlequin

O DuckDB gerado pelo pipeline fica em `dbt_db/fraud_warehouse.duckdb`. Para acessá-lo pelo terminal WSL:

```bash
# Modo leitura (sempre disponível — arquivo pertence ao container)
harlequin -a duckdb dbt_db/fraud_warehouse.duckdb --read-only

# Modo leitura e escrita (disponível após o próximo docker compose up)
harlequin -a duckdb dbt_db/fraud_warehouse.duckdb
```

> **Atalhos no Harlequin:** `Ctrl+Q` para sair, `Ctrl+Enter` para executar a query.

Schemas disponíveis no banco:
- `main` — modelos dbt materializados (`stg_fraud__transactions`, `amount`, `risk_score_average`)
- `main_elementary` — métricas e resultados de testes coletados pelo Elementary

## Comandos úteis

```bash
# Ver status dos serviços
docker compose ps

# Logs do Airflow em tempo real
docker compose logs -f airflow

# Reiniciar sem rebuild (preserva volumes)
docker compose down && docker compose up -d

# Rebuild completo (necessário após alterar Dockerfile ou requirements)
docker compose down && docker compose up -d --build
```

### Executar dbt manualmente (sem rodar a DAG)

```bash
# Rodar todos os modelos
docker compose exec airflow bash -lc 'cd /opt/airflow/dbt && /opt/dbt-venv/bin/dbt run --profiles-dir /opt/airflow/dbt'

# Rodar um modelo específico
docker compose exec airflow bash -lc 'cd /opt/airflow/dbt && /opt/dbt-venv/bin/dbt run --select stg_fraud__transactions --profiles-dir /opt/airflow/dbt'

# Rodar apenas os testes
docker compose exec airflow bash -lc 'cd /opt/airflow/dbt && /opt/dbt-venv/bin/dbt test --profiles-dir /opt/airflow/dbt'
```
