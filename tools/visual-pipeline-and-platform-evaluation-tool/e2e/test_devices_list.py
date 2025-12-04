"""Integration test covering the devices endpoint happy path.

Run with Python 3.12+ and pytest while the VIPPET API is available locally:

    python3.12 -m pytest e2e/test_devices_list.py

Environment variables:
* ``VIPPET_BASE_URL`` (default ``http://localhost/api/v1``)
* ``VIPPET_TEST_LOG_LEVEL`` (default ``INFO``)
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

import pytest
import requests

BASE_URL = os.environ.get("VIPPET_BASE_URL", "http://localhost/api/v1")
LOG_LEVEL_NAME = os.environ.get("VIPPET_TEST_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL_NAME, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("e2e.devices_list")

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def http_client() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()


def _fetch_devices(session: requests.Session) -> List[Dict[str, Any]]:
    logger.info("Fetching devices from %s", f"{BASE_URL}/devices")
    response = session.get(f"{BASE_URL}/devices", timeout=30)
    response.raise_for_status()
    payload = response.json()
    assert isinstance(payload, list), \
        f"Expected list response, got {type(payload).__name__}"
    logger.info("Retrieved %d devices", len(payload))
    return payload


def test_devices_endpoint_returns_devices(http_client: requests.Session) -> None:
    devices = _fetch_devices(http_client)

    assert devices, "Devices endpoint returned an empty list"
    sample = devices[0]
    assert isinstance(sample, dict), "Device entries must be objects"
    required_fields = [
        "device_name",
        "full_device_name",
        "device_type",
        "device_family",
        "gpu_id",
    ]
    for field in required_fields:
        assert field in sample, f"Device missing '{field}' field"
    str_fields = ["device_name", "full_device_name", "device_type", "device_family"]
    for field in str_fields:
        assert isinstance(sample[field], str) and sample[field], \
            f"Device field '{field}' must be a non-empty string"
    assert sample.get("gpu_id") is None or isinstance(sample["gpu_id"], int), \
        "Device field 'gpu_id' must be an integer or null"
