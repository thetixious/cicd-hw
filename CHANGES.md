# Changes

## ЛР 2. Airflow + Spark

- Добавлен Spark Standalone кластер из `spark-master` и `spark-worker` в `docker-compose.yml`.
- Образ Airflow расширен пакетами `procps`, `default-jre`, `apache-airflow-providers-apache-spark==4.1.1` и `pyspark==3.5.0`.
- Добавлена директория `spark/` с PySpark job `sales_metrics_spark_job.py`.
- Добавлен DAG `spark_sales_metrics`, который запускает PySpark job через `SparkSubmitOperator`.
- В Compose добавлено подключение Airflow `spark_local` через переменную `AIRFLOW_CONN_SPARK_LOCAL`.
- В volumes добавлены директории `dags`, `spark`, `logs` и `reports`.
