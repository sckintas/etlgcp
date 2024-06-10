from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyTableOperator
from airflow.utils.dates import days_ago

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

upload_to_gcs = BashOperator(
    task_id='upload_to_gcs',
    bash_command='python /opt/airflow/dags/load_csv_to_bigquery.py',
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
    bucket='airflowdbt',
    source_objects=['Online_Retail.csv'],
    destination_project_dataset_table='airflowetl-425915.retail.raw_invoices',
    skip_leading_rows=1,
    source_format='CSV',
    write_disposition='WRITE_TRUNCATE',
    field_delimiter=',',
    gcp_conn_id='gcp',
    dag=dag,
)

run_dbt_models = BashOperator(
    task_id='run_dbt_models',
    bash_command='cd /opt/airflow/dbt/retail && dbt run --profiles-dir /opt/airflow/dbt/retail',
    dag=dag,
)

upload_to_gcs >> create_retail_dataset >> create_retail_table >> gcs_to_bigquery >> run_dbt_models
