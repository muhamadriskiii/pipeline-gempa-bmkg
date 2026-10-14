from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

SRC = "/airflow/pipeline_gempa/src"

default_args = {
    "owner": "ris",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="gempa_idn",
    default_args=default_args,
    schedule="*/1 * * * *",
    start_date=datetime(2026, 10, 8),
    catchup=False,
    tags=["bmkg"],
) as dag:

    extract = BashOperator(task_id="extract", bash_command=f"python {SRC}/extract.py")
    transform = BashOperator(task_id="transform", bash_command=f"python {SRC}/transform.py")
    load = BashOperator(task_id="load", bash_command=f"python {SRC}/load.py")
    notify = BashOperator(task_id="notify", bash_command=f"python {SRC}/notify.py")

    extract >> transform >> load >> notify