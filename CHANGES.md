# Changes

## ЛР 3. Gitlab CI/CD

- Добавлен `.gitlab-ci.yml` с этапами `test`, `build` и `deploy`.
- Добавлена синтетическая test job, которая проверяет наличие директорий `dags/`, `spark/`, ключевых файлов и валидность `docker compose config`.
- Добавлен build job для сборки кастомного Airflow-образа `cicd-hw-airflow:2.7.1`.
- Добавлен deploy job, который автоматически запускается только для веток `main`, `master` и `develop`.
- Для веток с префиксом `feature/` build job сделан ручным, чтобы он не выполнялся автоматически.
- Все job привязаны к тегированному раннеру `devops-runner`.
- Добавлена ручная job `clear-deployment` для остановки развернутых compose-сервисов.

## ЛР 2. Airflow + Spark

- Добавлен Spark Standalone кластер из `spark-master` и `spark-worker` в `docker-compose.yml`.
- Образ Airflow расширен пакетами `procps`, `default-jre`, `apache-airflow-providers-apache-spark==4.1.1` и `pyspark==3.5.0`.
- Добавлена директория `spark/` с PySpark job `sales_metrics_spark_job.py`.
- Добавлен DAG `spark_sales_metrics`, который запускает PySpark job через `SparkSubmitOperator`.
- В Compose добавлено подключение Airflow `spark_local` через переменную `AIRFLOW_CONN_SPARK_LOCAL`.
- В volumes добавлены директории `dags`, `spark`, `logs` и `reports`.
