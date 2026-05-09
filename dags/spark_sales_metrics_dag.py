from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator


with DAG(
    dag_id="spark_sales_metrics",
    description="Runs a PySpark sales metrics job on the standalone Spark cluster.",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["homework", "spark", "sales"],
) as dag:
    SparkSubmitOperator(
        task_id="run_sales_metrics_spark_job",
        application="/opt/airflow/spark/sales_metrics_spark_job.py",
        application_args=["{{ ds }}"],
        name="sales_metrics_spark_job",
        conn_id="spark_local",
        verbose=True,
    )
