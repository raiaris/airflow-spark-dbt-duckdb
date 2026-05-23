import pyspark
import os

conf_dir = os.path.join(os.path.dirname(pyspark.__file__), "conf")
os.makedirs(conf_dir, exist_ok=True)
conf_file = os.path.join(conf_dir, "spark-defaults.conf")

with open(conf_file, "w") as f:
    f.write(
        "spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions\n"
        "spark.sql.catalog.local_iceberg=org.apache.iceberg.spark.SparkCatalog\n"
        "spark.sql.catalog.local_iceberg.type=hadoop\n"
        "spark.sql.catalog.local_iceberg.warehouse=/warehouse\n"
        "spark.sql.catalog.local_iceberg.io-impl=org.apache.iceberg.hadoop.HadoopFileIO\n"
        "spark.hadoop.fs.defaultFS=file:///\n"
        "spark.hadoop.fs.permissions.umask-mode=000\n"
    )

print("Created:", conf_file)
