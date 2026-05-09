FROM apache/airflow:2.7.1

WORKDIR /opt/airflow

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends procps default-jre \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
RUN pip3 install --no-cache-dir \
    apache-airflow-providers-apache-spark==4.1.1 \
    pyspark==3.5.0

COPY --chown=airflow:root dags/ /opt/airflow/dags/
COPY --chown=airflow:root spark/ /opt/airflow/spark/
