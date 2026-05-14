FROM apache/airflow:2.10.2

LABEL org.opencontainers.image.title="vortex-airflow"
LABEL org.opencontainers.image.description="Custom Airflow image for Vortex"

USER airflow
RUN pip install --no-cache-dir dbt-postgres==1.8.2
