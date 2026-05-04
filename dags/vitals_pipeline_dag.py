#!/Users/prathikshamohanrajeurs/anaconda3/bin/python3

# To orchestrate the full patient vitals anomaly detection pipeline

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Project path
PROJECT_PATH = '/Users/prathikshamohanrajeurs/Documents/patient-vitals-anomaly-detection'
PYTHON = '/Users/prathikshamohanrajeurs/anaconda3/bin/python3'
DBT = '/Users/prathikshamohanrajeurs/anaconda3/bin/dbt'

# Default arguments for all tasks
default_args = {
    'owner': 'prathiksha',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}

# Define the DAG
with DAG(
    dag_id='patient_vitals_anomaly_detection',
    default_args=default_args,
    description='End-to-end ICU vitals anomaly detection pipeline',
    schedule='@daily',
    catchup=False
) as dag:

    # Step 1 - Ingest raw data into MySQL
    ingest = BashOperator(
        task_id='ingest_data',
        bash_command=f'cd {PROJECT_PATH} && {PYTHON} src/ingest.py',
    )

    # Step 2 - Validate data quality
    validate = BashOperator(
        task_id='validate_data',
        bash_command=f'cd {PROJECT_PATH} && {PYTHON} src/validate.py',
    )

    # Step 3 - Engineer features
    features = BashOperator(
        task_id='engineer_features',
        bash_command=f'cd {PROJECT_PATH} && {PYTHON} src/features.py',
    )

    # Step 4 - Train Isolation Forest and generate anomaly scores
    train = BashOperator(
        task_id='train_model',
        bash_command=f'cd {PROJECT_PATH} && {PYTHON} src/train.py',
    )

    # Step 5 - Run dbt models to transform and summarize results
    dbt_run = BashOperator(
        task_id='dbt_transform',
        bash_command=f'cd {PROJECT_PATH}/dbt_project && {DBT} run',
    )

    # Step 6 - Visualize anomalies
    visualize = BashOperator(
        task_id='visualize_anomalies',
        bash_command=f'cd {PROJECT_PATH} && {PYTHON} src/visualize.py',
    )

    # Defining the order of execution
    ingest >> validate >> features >> train >> dbt_run >> visualize