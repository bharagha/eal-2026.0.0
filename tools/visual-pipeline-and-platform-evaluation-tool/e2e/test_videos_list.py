"""Integration test covering the videos endpoint happy path.

Run with Python 3.12+ and pytest while the VIPPET API is available locally:

    python3.12 -m pytest e2e/test_videos_list.py

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
logger = logging.getLogger("e2e.videos_list")

EXPECTED_VIDEOS: List[Dict[str, Any]] = [
    {
        "filename": "people.mp4",
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "frame_count": 302,
        "codec": "h264",
        "duration": 10.066666666666666,
    },
    {
        "filename": "license-plate-detection.mp4",
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "frame_count": 923,
        "codec": "h264",
        "duration": 30.766666666666666,
    },
]

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def http_client() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()


def _fetch_videos(session: requests.Session) -> List[Dict[str, Any]]:
    logger.info("Fetching videos from %%s", f"{BASE_URL}/videos")
    response = session.get(f"{BASE_URL}/videos", timeout=30)
    response.raise_for_status()
    payload = response.json()
    assert isinstance(payload, list), \
        f"Expected list response, got {type(payload).__name__}"
    logger.info("Retrieved %%d videos", len(payload))
    return payload


def _video_matches(candidate: Dict[str, Any], expected: Dict[str, Any]) -> bool:
    return all(candidate.get(key) == value for key, value in expected.items())


def test_videos_endpoint_returns_videos(http_client: requests.Session) -> None:
    videos = _fetch_videos(http_client)

    assert videos, "Videos endpoint returned an empty list"
    sample = videos[0]
    assert isinstance(sample, dict), "Video entries must be objects"
    required_fields = [
        "filename",
        "width",
        "height",
        "fps",
        "frame_count",
        "codec",
        "duration",
    ]
    for field in required_fields:
        assert field in sample, f"Video missing '{field}' field"
    assert isinstance(sample["filename"], str) and sample["filename"], \
        "Video filename must be a non-empty string"
    assert isinstance(sample["codec"], str) and sample["codec"], \
        "Video codec must be a non-empty string"
    numeric_fields = ["width", "height", "fps", "frame_count", "duration"]
    for field in numeric_fields:
        assert isinstance(sample[field], (int, float)), \
            f"Video field '{field}' must be numeric"

    for expected in EXPECTED_VIDEOS:
        matching = next((video for video in videos if _video_matches(video, expected)), None)
        assert matching is not None, \
            f"Videos endpoint missing expected entry: {expected['filename']}"
