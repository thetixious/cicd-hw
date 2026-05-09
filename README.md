# CI/CD homework

Репозиторий для лабораторных работ по DevOps.

## ЛР 3. Gitlab CI/CD

В ветке `hw3` добавлен GitLab CI/CD pipeline для проверки, сборки и деплоя стенда Airflow + Spark.

Ссылка на GitLab: https://gitlab.com/tix_pix/cicd-course/-/tree/hw3?ref_type=heads

Состав CI/CD:

- `.gitlab-ci.yml` описывает pipeline из стадий `test`, `build`, `deploy`.
- `test-project-structure` запускается всегда во всех ветках и проверяет наличие `dags/`, `spark/`, ключевых файлов и валидность `docker compose config`.
- `build-airflow-image` собирает Docker-образ `cicd-hw-airflow:2.7.1`.
- `deploy-airflow-spark` автоматически выполняет `docker compose up -d` только для веток `main`, `master` и `develop`.
- Для веток `feature/*` build job доступен только вручную и не стартует автоматически.
- Все job требуют GitLab Runner с тегом `devops-runner`.
- `clear-deployment` является ручной job для остановки контейнеров через `docker compose rm -sf`.

### Настройка GitLab Runner

Runner должен быть зарегистрирован для проекта с тегом:

```text
devops-runner
```

В настройках runner нужно разрешить запуск tagged jobs. Для работы Docker-команд runner должен иметь доступ к Docker socket:

```text
/var/run/docker.sock:/var/run/docker.sock
```

В `/etc/gitlab-runner/config.toml` у Docker runner должен быть volume:

```toml
volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache"]
```

После push ветки pipeline можно проверить в GitLab: `CI/CD -> Pipelines`.

## ЛР 2. Airflow + Spark

В ветке `hw2` подготовлен локальный деплой Apache Airflow и Spark Standalone через Docker Compose.

Состав решения:

- `Dockerfile` собирает кастомный образ на базе `apache/airflow:2.7.1`, устанавливает Java, `procps`, Spark provider и `pyspark`.
- `docker-compose.yml` поднимает `postgres`, `spark-master`, `spark-worker`, `airflow-init`, `airflow-webserver` и `airflow-scheduler`.
- `dags/spark_sales_metrics_dag.py` содержит DAG `spark_sales_metrics`, который запускает Spark job через `SparkSubmitOperator`.
- `spark/sales_metrics_spark_job.py` содержит PySpark job с использованием `SparkSession`.
- `reports/` используется Airflow для сохранения markdown-отчетов по результатам запуска DAG.
- `logs/` используется Airflow для логов выполнения задач.
- `CHANGES.md` содержит изменения по сравнению с ЛР 1.

### Что делает DAG

`spark_sales_metrics` состоит из одной Airflow-задачи `run_sales_metrics_spark_job`, которая отправляет Python-приложение в Spark-кластер.

Spark job:

1. Создает `SparkSession` с master `spark://spark-master:7077`.
2. Формирует тестовый набор заказов за логическую дату запуска.
3. Считает метрики продаж средствами `pyspark`: выручку, конверсию, средний чек, лучший продукт и выручку по продуктам.
4. Сохраняет markdown-отчет в `/opt/airflow/reports`, который проброшен в локальную директорию `reports`.

### Локальный запуск

Перед первым запуском создайте переменную `AIRFLOW_UID`, чтобы контейнеры корректно писали логи и отчеты:

```bash
echo "AIRFLOW_UID=$(id -u)" > .env
```

Запустите сервисы:

```bash
docker compose up -d --build
```

После старта должны работать два контейнера Airflow, один контейнер Postgres и два контейнера Spark:

```bash
docker compose ps
```

Airflow UI будет доступен по адресу:

```text
http://localhost:8080/
```

Spark Master UI будет доступен по адресу:

```text
http://localhost:4040/
```

Креды по умолчанию:

```text
login: airflow
password: airflow
```

Подключение Airflow к Spark создается автоматически через переменную окружения. В URI host закодирован, чтобы внутри Airflow connection он отображался как `spark://spark-master`, а port как `7077`:

```text
AIRFLOW_CONN_SPARK_LOCAL=spark://spark%3A%2F%2Fspark-master:7077
```

В UI включите DAG `spark_sales_metrics` и запустите его вручную или дождитесь планового запуска. После успешного выполнения отчет появится в директории `reports`, а в Spark UI будет виден воркер и выполненное приложение.

Запустить DAG из консоли можно так:

```bash
docker compose exec airflow-scheduler airflow dags test spark_sales_metrics 2026-05-09
```

Остановить стенд:

```bash
docker compose down
```

Удалить также данные Postgres:

```bash
docker compose down --volumes
```
