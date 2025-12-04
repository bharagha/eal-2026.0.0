"""Integration test ensuring the models endpoint responds with data.

Run with Python 3.12+ and pytest while the VIPPET API is available locally:

    python3.12 -m pytest e2e/test_models_list.py

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
logger = logging.getLogger("e2e.models_list")

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def http_client() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()


def _fetch_models(session: requests.Session) -> List[Dict[str, Any]]:
    logger.info("Fetching models from %%s", f"{BASE_URL}/models")
    response = session.get(f"{BASE_URL}/models", timeout=30)
    response.raise_for_status()
    payload = response.json()
    assert isinstance(payload, list), \
        f"Expected list response, got {type(payload).__name__}"
    logger.info("Retrieved %%d models", len(payload))
    return payload


def test_models_endpoint_returns_models(http_client: requests.Session) -> None:
    models = _fetch_models(http_client)

    assert models, "Models endpoint returned an empty list"
    sample = models[0]
    assert isinstance(sample, dict), "Model entries must be objects"
    assert sample.get("name"), "First model missing 'name' field"
    assert sample.get("display_name"), "First model missing 'display_name' field"
    assert sample.get("category"), "First model missing 'category' field"
    assert sample.get("precision"), "First model missing 'precision' field"
