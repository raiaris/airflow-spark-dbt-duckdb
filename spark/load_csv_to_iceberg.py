import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Argumentos passados pelo Airflow: <logical_date YYYY-MM-DD> <dagrun_id>
logical_date = sys.argv[1] if len(sys.argv) > 1 else "1970-01-01"
dagrun_id    = sys.argv[2] if len(sys.argv) > 2 else "manual"

year, month, day = (int(p) for p in logical_date.split("-"))

warehouse = "/warehouse"

spark = (
    SparkSession.builder.appName("load_csv_to_iceberg")
    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0")
    .config("spark.sql.catalog.local_iceberg", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.local_iceberg.type", "hadoop")
    .config("spark.sql.catalog.local_iceberg.warehouse", warehouse)
    .config("spark.sql.catalog.local_iceberg.io-impl", "org.apache.iceberg.hadoop.HadoopFileIO")
    .config("spark.hadoop.fs.defaultFS", "file:///")
    .config("spark.hadoop.fs.permissions.umask-mode", "000")
    .getOrCreate()
)

csv_path = "/data/df_fraud_credit.csv"

# Ler CSV com schema inferido
df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(csv_path)
)

# Função para converter 'none' em null em todas as colunas
def convert_none_to_null(df):
    for col_name in df.columns:
        df = df.withColumn(
            col_name,
            F.when(F.col(col_name) == 'none', None).otherwise(F.col(col_name))
        )
    return df

# Aplicar conversão de 'none' para null
df = convert_none_to_null(df)

# Adicionar colunas de partição
df = (
    df
    .withColumn("year",      F.lit(year))
    .withColumn("month",     F.lit(month))
    .withColumn("day",       F.lit(day))
    .withColumn("dagrun_id", F.lit(dagrun_id))
)

spark.sql("CREATE DATABASE IF NOT EXISTS local_iceberg.default")

(
    df.writeTo("local_iceberg.default.fraud_raw")
    .partitionedBy("year", "month", "day", "dagrun_id")
    .createOrReplace()
)

spark.stop()