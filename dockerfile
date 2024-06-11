FROM apache/airflow:2.5.1-python3.8

USER root

# Install Google Cloud SDK and PostgreSQL client
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sSL https://sdk.cloud.google.com | bash && \
    apt-get install -y postgresql-client

# Set environment variables
ENV AIRFLOW_HOME=/opt/airflow
ENV GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/gcp/service_account.json

# Copy Airflow DAGs and CSV file
COPY dags /opt/airflow/dags
COPY Online_Retail.csv /opt/airflow/

# Copy service account key
COPY gcp/service_account.json /opt/airflow/gcp/service_account.json

USER airflow

# Install Python dependencies and dbt
COPY constraints.txt /
RUN pip install --user apache-airflow[gcp] google-cloud-bigquery pandas psycopg2-binary "sqlalchemy<2.0" dbt-bigquery -c /constraints.txt

# Copy dbt project files
COPY retail /opt/airflow/dbt/retail

# Set environment variable for dbt profiles directory
ENV DBT_PROFILES_DIR=/opt/airflow/dbt/retail

# Ensure the correct ownership of dbt project files
USER root
RUN chown -R airflow:root /opt/airflow/dbt/retail

USER airflow
