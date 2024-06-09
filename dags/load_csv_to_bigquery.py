from airflow import DAG
from airflow.operators.python_operator import PythonOperator
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
    'upload_csv_to_gcs',
    default_args=default_args,
    description='Upload CSV file to GCS bucket',
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

upload_to_gcs_task
