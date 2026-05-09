FROM apache/airflow:2.7.1

WORKDIR /opt/airflow

COPY --chown=airflow:root dags/ /opt/airflow/dags/
