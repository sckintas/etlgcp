import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyTableOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago
from google.cloud import storage

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

dag = DAG(
    'upload_to_gcs_and_load_to_bigquery_with_dbt',
    default_args=default_args,
    description='Upload CSV to GCS, load to BigQuery, and run DBT models',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
)

def upload_to_gcs():
    key_path = '/opt/airflow/gcp/service_account.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path
    
    client = storage.Client()
    bucket_name = 'new_retail'  # Ensure this is the correct bucket name
    destination_blob_name = 'Online_Retail.csv'
    source_file_name = '/opt/airflow/Online_Retail.csv'
    
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    
    print(f"File {source_file_name} uploaded to {bucket_name}/{destination_blob_name}.")

def read_sql_file():
    with open('/opt/airflow/dags/country.sql', 'r') as file:
        sql_content = file.read()
    return sql_content

upload_to_gcs_task = PythonOperator(
    task_id='upload_to_gcs',
    python_callable=upload_to_gcs,
    dag=dag,
)

create_retail_dataset = BigQueryCreateEmptyDatasetOperator(
    task_id='create_retail_dataset',
    dataset_id='retail',
    gcp_conn_id='gcp',
    dag=dag,
)

create_retail_table = BigQueryCreateEmptyTableOperator(
    task_id='create_retail_table',
    dataset_id='retail',
    table_id='raw_invoices',
    schema_fields=[
        {"name": "InvoiceNo", "type": "STRING", "mode": "NULLABLE"},
        {"name": "StockCode", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Description", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Quantity", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "InvoiceDate", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "UnitPrice", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "CustomerID", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "Country", "type": "STRING", "mode": "NULLABLE"},
    ],
    gcp_conn_id='gcp',
    dag=dag,
)

gcs_to_bigquery = GCSToBigQueryOperator(
    task_id='gcs_to_bigquery',
    bucket='new_retail',  # Ensure this matches the bucket used in upload_to_gcs
    source_objects=['Online_Retail.csv'],
    destination_project_dataset_table='airflowetl-426020.retail.raw_invoices',
    skip_leading_rows=1,
    source_format='CSV',
    write_disposition='WRITE_TRUNCATE',
    field_delimiter=',',
    gcp_conn_id='gcp',
    dag=dag,
)

create_country_table = BigQueryInsertJobOperator(
    task_id='create_country_table',
    configuration={
        "query": {
            "query": read_sql_file(),
            "useLegacySql": False,
        }
    },
    gcp_conn_id='gcp',
    dag=dag,
)

run_dbt_models = BashOperator(
    task_id='run_dbt_models',
    bash_command='cd /opt/airflow/dbt/retail && dbt run --profiles-dir /opt/airflow/dbt/retail',
    dag=dag,
)

upload_to_gcs_task >> create_retail_dataset >> create_retail_table >> gcs_to_bigquery >> create_country_table >> run_dbt_models
