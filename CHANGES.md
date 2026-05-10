# Changes

## ЛР 4. Loki + Prometheus + Grafana

- Добавлены сервисы `loki`, `alloy`, `prometheus` и `grafana` в `docker-compose.yml`.
- Добавлен `alloy.conf` для отправки Airflow logs и Spark event logs в Loki.
- Добавлен `prometheus.yml` для сбора метрик Airflow, Spark master и Spark worker.
- Добавлен `spark/metrics.properties` для включения Spark Prometheus servlet.
- В Airflow image добавлен `airflow-exporter==1.5.3` для endpoint `/admin/metrics/`.
- В `spark_sales_metrics` включено Spark event logging в директорию `spark-events/`.
- Добавлен Grafana provisioning для datasources Prometheus/Loki и dashboard `Lab 4 Observability`.
- В `.gitlab-ci.yml` убрана временная диагностика Docker socket из build job.

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
