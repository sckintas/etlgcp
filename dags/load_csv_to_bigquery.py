from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyTableOperator
from airflow.utils.dates import days_ago
from google.cloud import storage
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

dag = DAG(
    'upload_to_gcs_and_load_to_bigquery',
    default_args=default_args,
    description='Upload CSV to GCS and load to BigQuery',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
)

def upload_to_gcs():
    key_path = '/opt/airflow/gcp/service_account.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path
    
    client = storage.Client()
    bucket_name = 'airflowdbt'
    destination_blob_name = 'Online_Retail.csv'
    source_file_name = '/opt/airflow/Online_Retail.csv'
    
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    
    print(f"File {source_file_name} uploaded to {bucket_name}/{destination_blob_name}.")

upload_to_gcs_task = PythonOperator(
    task_id='upload_to_gcs',
    python_callable=upload_to_gcs,
    dag=dag,
)

create_retail_dataset = BigQueryCreateEmptyDatasetOperator(
    task_id='create_retail_dataset',
    dataset_id='retail_dataset',
    gcp_conn_id='gcp',  # Ensure this matches the connection ID in Airflow
    dag=dag,
)

create_retail_table = BigQueryCreateEmptyTableOperator(
    task_id='create_retail_table',
    dataset_id='retail_dataset',
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
    gcp_conn_id='gcp',  # Ensure this matches the connection ID in Airflow
    dag=dag,
)

gcs_to_bigquery_task = GCSToBigQueryOperator(
    task_id='gcs_to_bigquery',
    bucket='airflowdbt',
    source_objects=['Online_Retail.csv'],
    destination_project_dataset_table='airflowetl-425915.retail_dataset.raw_invoices',
    skip_leading_rows=1,
    source_format='CSV',
    write_disposition='WRITE_TRUNCATE',
    field_delimiter=',',
    gcp_conn_id='gcp',  # Ensure this is set to the correct connection ID
    ignore_unknown_values=True,
    max_bad_records=5000,  # Further increase the limit of bad records
    dag=dag,
)

upload_to_gcs_task >> create_retail_dataset >> create_retail_table >> gcs_to_bigquery_task
