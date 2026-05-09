# CI/CD homework

Репозиторий для лабораторных работ по DevOps/CI/CD.

## ЛР 1. Airflow + docker compose

В ветке `hw1` подготовлен локальный деплой Apache Airflow через Docker Compose.

Состав решения:

- `Dockerfile` собирает кастомный образ на базе `apache/airflow:2.7.1` и копирует DAG в рабочую директорию Airflow `/opt/airflow`.
- `docker-compose.yml` поднимает `postgres`, `airflow-init`, `airflow-webserver` и `airflow-scheduler`.
- `dags/sales_metrics_dag.py` содержит DAG `daily_sales_metrics`.
- `reports/` используется Airflow для сохранения markdown-отчетов по результатам запуска DAG.
- `logs/` используется Airflow для логов выполнения задач.

### Что делает DAG

`daily_sales_metrics` состоит из четырех задач:

1. `extract_orders` формирует тестовый набор заказов за логическую дату запуска.
2. `calculate_metrics` считает выручку, конверсию, средний чек, среднее количество товаров и лучший продукт.
3. `check_targets` проверяет рассчитанные метрики относительно простых целевых значений.
4. `write_report` сохраняет отчет в `/opt/airflow/reports`, который проброшен в локальную директорию `reports`.

Такой DAG выполняет несколько связанных шагов и считает бизнес-метрики, поэтому он сложнее примера `Hello world`.

### Локальный запуск

Перед первым запуском создайте переменную `AIRFLOW_UID`, чтобы контейнеры корректно писали логи и отчеты:

```bash
echo "AIRFLOW_UID=$(id -u)" > .env
```

Запустите сервисы:

```bash
docker compose up -d --build
```

После старта должны работать два контейнера Airflow и один контейнер Postgres:

```bash
docker compose ps
```

Airflow UI будет доступен по адресу:

```text
http://localhost:8080/
```

Креды по умолчанию:

```text
login: airflow
password: airflow
```

В UI включите DAG `daily_sales_metrics` и запустите его вручную или дождитесь планового запуска. После успешного выполнения отчет появится в директории `reports`.

Остановить стенд:

```bash
docker compose down
```

Удалить также данные Postgres:

```bash
docker compose down --volumes
```
