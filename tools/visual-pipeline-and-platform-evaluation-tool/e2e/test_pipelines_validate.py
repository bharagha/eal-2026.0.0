"""Integration test covering the pipelines validate endpoint.

Run with Python 3.12+ and pytest while the VIPPET API is available locally:

    python3.12 -m pytest e2e/test_pipelines_validate.py

Environment variables:
* ``VIPPET_BASE_URL`` (default ``http://localhost/api/v1``)
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
logger = logging.getLogger("e2e.pipelines_validate")

pytestmark = pytest.mark.integration

VALIDATION_PAYLOAD: Dict[str, Any] = {
    "type": "GStreamer",
    "pipeline_graph": {
        "nodes": [
            {"id": "0", "type": "videotestsrc", "data": {}},
            {"id": "1", "type": "videoconvert", "data": {}},
            {"id": "2", "type": "fakesink", "data": {}},
        ],
        "edges": [
            {"id": "0", "source": "0", "target": "1"},
            {"id": "1", "source": "1", "target": "2"},
        ],
    },
    "parameters": {"max-runtime": 10},
}


@pytest.fixture(scope="module")
def http_client() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()


def test_pipeline_validate_job_completes(http_client: requests.Session) -> None:
    logger.info("Submitting validation job to %%s", f"{BASE_URL}/pipelines/validate")
    response = http_client.post(
        f"{BASE_URL}/pipelines/validate",
        json=VALIDATION_PAYLOAD,
        timeout=60,
    )
    assert response.status_code == 202, (
        f"Validation endpoint returned {response.status_code}, body={response.text}"
    )
    payload = response.json()
    assert isinstance(payload, dict), "Validation response must be an object"
    job_id = payload.get("job_id")
    assert isinstance(job_id, str) and job_id, "Validation response missing job_id"
    logger.info("Validation job accepted with id %s", job_id)

    deadline = time.time() + POLL_TIMEOUT_SECONDS
    status_url = f"{BASE_URL}/jobs/validation/{job_id}/status"
    last_status: Dict[str, Any] | None = None
    while time.time() < deadline:
        response = http_client.get(status_url, timeout=30)
        response.raise_for_status()
        last_status = response.json()
        state = last_status.get("state")
        logger.info(
            "Validation job %s polled state=%s is_valid=%s",
            job_id,
            state,
            last_status.get("is_valid"),
        )
        if state == "COMPLETED":
            break
        time.sleep(POLL_INTERVAL_SECONDS)

    assert last_status is not None, "Validation job status polling produced no data"
    assert last_status.get("state") == "COMPLETED", (
        f"Validation job {job_id} finished in unexpected state {last_status.get('state')}"
    )
    assert last_status.get("is_valid") is True, (
        f"Validation job {job_id} expected is_valid=True, got {last_status.get('is_valid')}"
    )
