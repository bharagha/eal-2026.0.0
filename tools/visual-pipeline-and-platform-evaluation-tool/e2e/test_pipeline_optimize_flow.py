"""Integration test covering pipeline optimization flows.

Run with Python 3.12+ and pytest while the VIPPET API is available locally:

    python3.12 -m pytest e2e/test_pipeline_optimize_flow.py

Environment variables:
* ``VIPPET_BASE_URL`` (default ``http://localhost/api/v1``)
* ``VIPPET_JOB_TIMEOUT_SECONDS`` (default ``600``)
* ``VIPPET_JOB_POLL_INTERVAL`` (default ``2.0``)
* ``VIPPET_TEST_LOG_LEVEL`` (default ``INFO``)
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict

import pytest
import requests

BASE_URL = os.environ.get("VIPPET_BASE_URL", "http://localhost/api/v1")
POLL_TIMEOUT_SECONDS = int(os.environ.get("VIPPET_JOB_TIMEOUT_SECONDS", "600"))
POLL_INTERVAL_SECONDS = float(os.environ.get("VIPPET_JOB_POLL_INTERVAL", "2.0"))
LOG_LEVEL_NAME = os.environ.get("VIPPET_TEST_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL_NAME, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("e2e.pipeline_optimize_flow")

pytestmark = pytest.mark.integration

PIPELINE_NAME = "Simple Video Structurization (D-T-C) [CPU]"
OPTIMIZATION_CASES = [
    (
        "preprocess",
        {
            "type": "preprocess",
            "parameters": {"search_duration": 30, "sample_duration": 5},
        },
    ),
    (
        "optimize",
        {
            "type": "optimize",
            "parameters": {"search_duration": 30, "sample_duration": 5},
        },
    ),
]


@pytest.fixture(scope="module")
def http_client() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()


def _fetch_pipeline_id(session: requests.Session, pipeline_name: str) -> str:
    logger.info("Fetching pipeline id for '%s'", pipeline_name)
    response = session.get(f"{BASE_URL}/pipelines", timeout=30)
    response.raise_for_status()
    pipelines: list[Dict[str, Any]] = response.json()
    matching = next((p for p in pipelines if p.get("name") == pipeline_name), None)
    assert matching is not None, (
        f"Pipeline named '{pipeline_name}' not found in /pipelines response"
    )
    pipeline_id = matching.get("id")
    assert pipeline_id, "Matching pipeline missing 'id' field"
    logger.info("Using pipeline id %s for '%s'", pipeline_id, pipeline_name)
    return str(pipeline_id)


def _start_optimization_job(
    session: requests.Session,
    pipeline_id: str,
    payload: Dict[str, Any],
) -> str:
    logger.info(
        "Starting pipeline optimization for id=%s case=%s",
        pipeline_id,
        payload.get("type"),
    )
    response = session.post(
        f"{BASE_URL}/pipelines/{pipeline_id}/optimize",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    job_id = response.json().get("job_id")
    assert job_id, "Optimization response missing 'job_id'"
    logger.info("Optimization job started: %s", job_id)
    return str(job_id)


def _get_job_status(session: requests.Session, job_id: str) -> Dict[str, Any]:
    response = session.get(
        f"{BASE_URL}/jobs/optimization/{job_id}/status",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def _wait_for_completion(session: requests.Session, job_id: str) -> Dict[str, Any]:
    deadline = time.time() + POLL_TIMEOUT_SECONDS
    first_status = _get_job_status(session, job_id)
    assert first_status.get("state") in {"RUNNING", "COMPLETED"}, (
        "Unexpected initial job state "
        f"{first_status.get('state')} for optimization job {job_id}"
    )
    logger.info(
        "Job %s initial state %s (elapsed=%sms)",
        job_id,
        first_status.get("state"),
        first_status.get("elapsed_time"),
    )
    if first_status.get("state") == "COMPLETED":
        logger.info("Job %s completed before polling loop", job_id)
        return first_status

    last_status = first_status

    while time.time() < deadline:
        if last_status.get("state") == "COMPLETED":
            logger.info("Job %s finished with COMPLETED state", job_id)
            return last_status
        time.sleep(POLL_INTERVAL_SECONDS)
        last_status = _get_job_status(session, job_id)
        logger.info(
            "Job %s polled state=%s error=%s",
            job_id,
            last_status.get("state"),
            last_status.get("error_message"),
        )

    pytest.fail(
        f"Optimization job {job_id} did not reach COMPLETED within {POLL_TIMEOUT_SECONDS} seconds"
    )


@pytest.mark.parametrize("case_id,payload", OPTIMIZATION_CASES, ids=[c[0] for c in OPTIMIZATION_CASES])
def test_pipeline_optimize_flow(
    http_client: requests.Session,
    case_id: str,
    payload: Dict[str, Any],
) -> None:
    logger.info("Running pipeline optimize flow case '%s'", case_id)
    pipeline_id = _fetch_pipeline_id(http_client, PIPELINE_NAME)
    job_id = _start_optimization_job(http_client, pipeline_id, payload)
    final_status = _wait_for_completion(http_client, job_id)

    assert final_status.get("state") == "COMPLETED", (
        f"Job {job_id} finished in unexpected state {final_status.get('state')}"
    )
    assert final_status.get("error_message") is None, (
        f"Job {job_id} returned error message: {final_status.get('error_message')}"
    )
