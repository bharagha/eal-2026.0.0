"""
Unit tests for validator.py (GStreamer Pipeline Validator).

These tests focus on the Python control flow and error handling, using
mocking to avoid depending on real GStreamer behavior where possible.
"""

import unittest
from typing import Any, Tuple
from unittest import mock

import validator


class TestParseArgs(unittest.TestCase):
    """Tests for the parse_args helper."""

    def test_parse_args_basic(self) -> None:
        """parse_args should correctly parse max-runtime, log-level and pipeline."""
        args = validator.parse_args(
            [
                "--max-runtime",
                "5",
                "--log-level",
                "DEBUG",
                "videotestsrc",
                "!",
                "fakesink",
            ]
        )

        self.assertEqual(args.max_runtime, 5.0)
        self.assertEqual(args.log_level, "DEBUG")
        self.assertEqual(args.pipeline, ["videotestsrc", "!", "fakesink"])


class TestParsePipeline(unittest.TestCase):
    """Tests for the parse_pipeline helper."""

    @mock.patch.object(validator, "Gst")
    def test_parse_pipeline_failure(self, mock_gst: Any) -> None:
        """parse_pipeline should return (None, False) when Gst.parse_launch raises."""
        mock_gst.parse_launch.side_effect = RuntimeError("parse error")

        pipeline, ok = validator.parse_pipeline("invalid pipeline ! element")

        self.assertIsNone(pipeline)
        self.assertFalse(ok)

    @mock.patch.object(validator, "Gst")
    def test_parse_pipeline_success(self, mock_gst: Any) -> None:
        """parse_pipeline should return (pipeline, True) on success."""
        fake_pipeline = object()
        mock_gst.parse_launch.return_value = fake_pipeline

        pipeline, ok = validator.parse_pipeline("videotestsrc ! fakesink")
        self.assertIs(pipeline, fake_pipeline)
        self.assertTrue(ok)


class TestValidatePipeline(unittest.TestCase):
    """Tests for the validate_pipeline high-level helper."""

    def test_validate_pipeline_failure_on_parse(self) -> None:
        """validate_pipeline should return False if parsing fails."""

        def fake_parse_pipeline(_desc: str) -> Tuple[None, bool]:
            return None, False

        with mock.patch.object(validator, "parse_pipeline", fake_parse_pipeline):
            self.assertFalse(
                validator.validate_pipeline("invalid pipeline", max_run_time_sec=1.0)
            )

    def test_validate_pipeline_success_on_eos(self) -> None:
        """validate_pipeline should return True if parse and run both succeed (EOS)."""

        fake_pipeline = object()

        def fake_parse_pipeline(_desc: str):
            return fake_pipeline, True

        def fake_run_pipeline_for_short_validation(pipeline, max_run_time_sec):
            self.assertIs(pipeline, fake_pipeline)
            self.assertEqual(max_run_time_sec, 2.0)
            # True, None -> success via EOS or equivalent
            return True, None

        with (
            mock.patch.object(validator, "parse_pipeline", fake_parse_pipeline),
            (
                mock.patch.object(
                    validator,
                    "run_pipeline_for_short_validation",
                    fake_run_pipeline_for_short_validation,
                )
            ),
        ):
            self.assertTrue(
                validator.validate_pipeline(
                    "videotestsrc ! fakesink", max_run_time_sec=2.0
                )
            )

    def test_validate_pipeline_success_on_timeout(self) -> None:
        """Timeout should be treated as SUCCESS by validate_pipeline."""

        fake_pipeline = object()

        def fake_parse_pipeline(_desc: str):
            return fake_pipeline, True

        def fake_run_pipeline_for_short_validation(pipeline, max_run_time_sec):
            self.assertIs(pipeline, fake_pipeline)
            # True, "timeout" -> success via timeout (no error observed)
            return True, "timeout"

        with (
            mock.patch.object(validator, "parse_pipeline", fake_parse_pipeline),
            (
                mock.patch.object(
                    validator,
                    "run_pipeline_for_short_validation",
                    fake_run_pipeline_for_short_validation,
                )
            ),
        ):
            self.assertTrue(
                validator.validate_pipeline(
                    "videotestsrc ! fakesink", max_run_time_sec=1.0
                )
            )

    def test_validate_pipeline_failure_on_run_error(self) -> None:
        """validate_pipeline should return False if run_pipeline_for_short_validation fails."""

        fake_pipeline = object()

        def fake_parse_pipeline(_desc: str):
            return fake_pipeline, True

        def fake_run_pipeline_for_short_validation(pipeline, max_run_time_sec):
            self.assertIs(pipeline, fake_pipeline)
            # False, "error" -> runtime error observed
            return False, "error"

        with (
            mock.patch.object(validator, "parse_pipeline", fake_parse_pipeline),
            (
                mock.patch.object(
                    validator,
                    "run_pipeline_for_short_validation",
                    fake_run_pipeline_for_short_validation,
                )
            ),
        ):
            self.assertFalse(
                validator.validate_pipeline(
                    "videotestsrc ! fakesink", max_run_time_sec=1.0
                )
            )


class TestMain(unittest.TestCase):
    """Tests for the main CLI entry point using dependency injection.

    We test run_application(), which lets us inject fake
    initialize_gst_fn and validate_fn implementations. This way we can
    fully exercise main's control flow without requiring a real GStreamer
    installation in the unit test environment.
    """

    def test_main_success(self) -> None:
        """run_application should return 0 when validation succeeds."""

        def fake_initialize_gst() -> None:
            # No-op: pretend GStreamer initialized successfully.
            return None

        def fake_validate(pipeline_description: str, max_run_time_sec: float) -> bool:
            # We can assert that arguments are passed correctly if we want.
            self.assertIn("videotestsrc", pipeline_description)
            self.assertEqual(max_run_time_sec, 3.0)
            return True

        exit_code = validator.run_application(
            argv=[
                "--max-runtime",
                "3",
                "--log-level",
                "INFO",
                "videotestsrc",
                "!",
                "fakesink",
            ],
            initialize_gst_fn=fake_initialize_gst,
            validate_fn=fake_validate,
        )

        self.assertEqual(exit_code, 0)

    def test_main_failure(self) -> None:
        """run_application should return 1 when validation fails."""

        def fake_initialize_gst() -> None:
            return None

        def fake_validate(_desc: str, _max_run_time_sec: float) -> bool:
            return False

        exit_code = validator.run_application(
            argv=[
                "--max-runtime",
                "3",
                "--log-level",
                "INFO",
                "videotestsrc",
                "!",
                "fakesink",
            ],
            initialize_gst_fn=fake_initialize_gst,
            validate_fn=fake_validate,
        )

        self.assertEqual(exit_code, 1)

    def test_main_internal_error(self) -> None:
        """run_application should return 1 when validate_fn raises."""

        def fake_initialize_gst() -> None:
            return None

        def fake_validate(_desc: str, _max_run_time_sec: float) -> bool:
            raise RuntimeError("unexpected")

        exit_code = validator.run_application(
            argv=[
                "--max-runtime",
                "3",
                "--log-level",
                "INFO",
                "videotestsrc",
                "!",
                "fakesink",
            ],
            initialize_gst_fn=fake_initialize_gst,
            validate_fn=fake_validate,
        )

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
