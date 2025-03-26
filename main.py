import functions_framework
from cloudevents.http.event import CloudEvent

import os
import logging

from google.cloud import run_v2


logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s | %(name)s | %(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)


def get_dbt_command(file_path, allowed_banks):
    """Determine the dbt command based on the file path.

    The path has the following format: {source_type}/{bank_name}/{file_name}.
    The source_type can be either 'statements' or 'bills'.
    """
    source_type, bank_name = file_path.lower().split("/")[0:2]
    if source_type not in ["statements", "bills"]:
        raise ValueError(f"Invalid source type: {source_type}")
    if bank_name not in allowed_banks:
        raise ValueError(f"Invalid bank name: {bank_name}")
    return ["run", "--select", f"{source_type}__{bank_name}+"]


@functions_framework.cloud_event
def process_new_file(event: CloudEvent) -> None:
    bucket_name = event.data["bucket"]
    file_path = event.data["name"]
    logger.info(f"Processing new file: gs://{bucket_name}/{file_path}")

    project_id = os.getenv("PROJECT_ID")
    region = os.getenv("REGION")
    job_name = os.getenv("CLOUD_RUN_JOB_NAME")

    job_path = f"projects/{project_id}/locations/{region}/jobs/{job_name}"
    dbt_command = get_dbt_command(file_path)

    client = run_v2.JobsClient()
    try:
        job_execution = client.run_job(
            run_v2.RunJobRequest(
                name=job_path,
                overrides=run_v2.RunJobRequest.Overrides(
                    container_overrides=[
                        run_v2.RunJobRequest.Overrides.ContainerOverride(
                            name=os.getenv("CLOUD_RUN_CONTAINER_NAME"),
                            args=dbt_command,
                        )
                    ]
                ),
            )
        )
        logger.info(f"Submitted dbt job with command: {dbt_command}")
        response = job_execution.result()
        logger.info(f"dbt job completed with status: {response}")
    except Exception as e:
        logger.error(f"Error triggering dbt job: {e}")
        raise e
