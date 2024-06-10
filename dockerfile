FROM apache/airflow:2.5.1

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

# Install Python dependencies and dbt
RUN pip install apache-airflow[gcp] google-cloud-bigquery pandas psycopg2-binary sqlalchemy<2.0 dbt-bigquery

USER airflow

# Copy dbt project files
COPY dbt_project /dbt
