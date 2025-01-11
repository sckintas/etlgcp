# README

## Purpose

This project is designed to automate a data pipeline using Airflow, Google Cloud Platform (GCP), and DBT (Data Build Tool). The pipeline includes uploading a CSV file to Google Cloud Storage (GCS), loading it into BigQuery, creating datasets and tables, and running DBT models for further transformations and analytics.

## Workflow Steps

1. **Upload CSV to GCS**:
   - Uploads the `Online_Retail.csv` file from the Airflow instance to a specified GCS bucket.

2. **Create BigQuery Dataset and Table**:
   - Creates a dataset named `retail` in BigQuery.
   - Creates a table named `raw_invoices` with a specified schema.

3. **Load Data into BigQuery**:
   - Loads the data from the uploaded CSV file in GCS into the `raw_invoices` table.

4. **Create Country Table**:
   - Executes a SQL query stored in `country.sql` to create a transformed table in BigQuery.

5. **Run DBT Models**:
   - Executes DBT models located in the `dbt/retail` directory for further transformations and analytics.

## Prerequisites

### Tools and Technologies
- **Airflow** (Dockerized setup)
- **Google Cloud Platform (GCP)**:
  - BigQuery
  - Google Cloud Storage (GCS)
- **DBT**

### Environment Setup

#### Dockerized Airflow
1. Install Docker and Docker Compose.
2. Set up an Airflow Docker environment by creating a `docker-compose.yml` file with necessary configurations.
3. Start the Airflow services:
   ```bash
   docker-compose up -d
   ```

#### GCP Configuration
1. Create a GCS bucket named `new_retail`.
2. Set up a service account with permissions for BigQuery and GCS.
3. Save the service account key JSON file to `/opt/airflow/gcp/service_account.json`.

#### DBT Setup
1. Install DBT in the Airflow container or in a separate environment.
2. Place the DBT project in `/opt/airflow/dbt/retail`.
3. Configure the `profiles.yml` file in `/opt/airflow/dbt/retail` to connect to your BigQuery project.

## File Structure

```
/opt/airflow/
├── dags/
│   ├── load_csv_to_bigquery.py  
│   ├── country.sql                                                        
├── Online_Retail.csv                                  
├── gcp/
│   └── service_account.json                       
├── dbt/
│   └── retail/
│       ├── dbt_project.yml                           
│       ├── profiles.yml                              
│       ├── models/
│       │   ├── sources/
│       │   │   └── sources.yml                       
│       │   ├── transform/
│       │   │   ├── dim_customer.sql                 
│       │   │   ├── dim_datetime.sql                 
│       │   │   ├── dim_product.sql                   
│       │   │   └── fct_invoices.sql                
│       ├── analyses/
│       ├── macros/
│       ├── seeds/
│       ├── snapshots/
│       ├── tests/
│       └── README.md                                 
├──Online_Retail.csv
├──.gitignore
├──constraints.txt
├──docker-compose.yml
├──dockerfile
├──requirements.txt

## Workflow Configuration

### Airflow DAG Configuration
- **DAG Name**: `upload_to_gcs_and_load_to_bigquery_with_dbt`
- **Default Arguments**:
  - Retries: 1
  - Owner: Airflow
- **Schedule**: None (manual trigger)
- **Start Date**: One day ago

### Variables
- **`bucket_name`**: The GCS bucket name (`new_retail`).
- **`source_file_name`**: Path to the CSV file (`/opt/airflow/Online_Retail.csv`).
- **`dataset_id`**: BigQuery dataset ID (`retail`).
- **`table_id`**: BigQuery table ID (`raw_invoices`).
- **`destination_project_dataset_table`**: Fully qualified BigQuery table name (`PROJECT_ID.retail.raw_invoices`).

## Execution

1. Place the `Online_Retail.csv` file in the `/opt/airflow/` directory.
2. Start the Airflow scheduler and webserver:
   ```bash
   docker-compose up -d
   ```
3. Trigger the DAG `upload_to_gcs_and_load_to_bigquery_with_dbt` from the Airflow UI or CLI.
4. Monitor the DAG execution.

## DAG Tasks

### Task 1: Upload to GCS
Uploads the `Online_Retail.csv` file to the GCS bucket `new_retail`.

### Task 2: Create BigQuery Dataset
Creates a BigQuery dataset named `retail`.

### Task 3: Create BigQuery Table
Creates a BigQuery table `raw_invoices` with a schema suitable for the uploaded CSV.

### Task 4: Load Data to BigQuery
Loads the CSV data into the `raw_invoices` table in BigQuery.

### Task 5: Create Country Table
Runs the SQL query in `country.sql` to create a table with specific transformations in BigQuery.

### Task 6: Run DBT Models
Executes DBT models to perform advanced analytics and transformations.

## DBT Models

### Sources
The `sources.yml` file in the `models/sources/` folder defines the data sources used by the DBT project. This includes:
- Source for raw invoice data loaded into BigQuery.

### Transformations
The `models/transform/` folder contains SQL files for data transformations:
1. **`dim_customer.sql`**:
   - Creates a dimension table for customer data with cleaned and deduplicated entries.

2. **`dim_datetime.sql`**:
   - Creates a dimension table for date and time attributes for analytics.

3. **`dim_product.sql`**:
   - Creates a dimension table for product-related information.

4. **`fct_invoices.sql`**:
   - Creates a fact table for invoice data, combining dimensions for analytics.

## Troubleshooting

### Common Issues
1. **GCS Upload Failure**:
   - Verify the service account key and permissions.
   - Check the bucket name and file paths.

2. **BigQuery Dataset/Table Creation Issues**:
   - Ensure the `gcp_conn_id` in Airflow matches your GCP connection.

3. **DBT Model Execution Failure**:
   - Validate the DBT project structure and profiles.
   - Ensure the BigQuery tables exist before running DBT.

### Logs and Debugging
- Check Airflow task logs in the Airflow UI for detailed error messages.

## Notes
- Update the `destination_project_dataset_table` with your actual GCP project ID.
- Customize the schema and DBT models based on your specific use case.


