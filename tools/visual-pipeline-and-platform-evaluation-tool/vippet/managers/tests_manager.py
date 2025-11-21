import logging
import sys
import threading
import time
from typing import Dict, Optional, List
from dataclasses import dataclass
import uuid

from api.api_schemas import (
    DensityJobSummary,
    DensityTestSpec,
    PerformanceJobSummary,
    PerformanceTestSpec,
    TestJobState,
    PipelinePerformanceSpec,
    PerformanceJobStatus,
    DensityJobStatus,
    TestsJobStatus,
)
from pipeline_runner import PipelineRunner
from benchmark import Benchmark
from managers.pipeline_manager import get_pipeline_manager

logger = logging.getLogger("tests_manager")

pipeline_manager = get_pipeline_manager()

# Singleton instance for TestsManager
_tests_manager_instance: Optional["TestsManager"] = None


def get_tests_manager() -> "TestsManager":
    """
    Return the singleton instance of :class:`TestsManager`.

    The first call lazily creates the instance.  If initialization fails
    for any reason the error is logged and the process is terminated.
    """
    global _tests_manager_instance
    if _tests_manager_instance is None:
        try:
            _tests_manager_instance = TestsManager()
        except Exception as e:
            logger.error(f"Failed to initialize TestsManager: {e}")
            sys.exit(1)
    return _tests_manager_instance


@dataclass
class PerformanceJob:
    id: str
    request: PerformanceTestSpec
    state: TestJobState
    start_time: int
    end_time: Optional[int] = None
    total_fps: Optional[float] = None
    per_stream_fps: Optional[float] = None
    total_streams: Optional[int] = None
    streams_per_pipeline: Optional[List[PipelinePerformanceSpec]] = None
    error_message: Optional[str] = None


@dataclass
class DensityJob:
    id: str
    request: DensityTestSpec
    state: TestJobState
    start_time: int
    end_time: Optional[int] = None
    total_fps: Optional[float] = None
    per_stream_fps: Optional[float] = None
    total_streams: Optional[int] = None
    streams_per_pipeline: Optional[List[PipelinePerformanceSpec]] = None
    error_message: Optional[str] = None


class TestsManager:
    def __init__(self):
        # All known jobs keyed by job id
        self.jobs: Dict[str, PerformanceJob | DensityJob] = {}
        # Currently running PipelineRunner or Benchmark jobs keyed by job id
        self.runners: Dict[str, PipelineRunner | Benchmark] = {}
        # Shared lock protecting access to ``jobs`` and ``runners``
        self.lock = threading.Lock()
        self.logger = logging.getLogger("TestsManager")

    @staticmethod
    def _generate_job_id() -> str:
        """
        Generate a unique job ID using UUID.
        """
        return uuid.uuid1().hex

    def _start_job(
        self,
        test_request: PerformanceTestSpec | DensityTestSpec,
        target_func,
    ) -> str:
        """Helper to start a performance or density test and return the job ID."""
        job_id = self._generate_job_id()

        # Create job record
        job: PerformanceJob | DensityJob
        if isinstance(test_request, PerformanceTestSpec):
            job = PerformanceJob(
                id=job_id,
                request=test_request,
                state=TestJobState.RUNNING,
                start_time=int(time.time() * 1000),  # milliseconds
            )
        else:  # DensityTestSpec
            job = DensityJob(
                id=job_id,
                request=test_request,
                state=TestJobState.RUNNING,
                start_time=int(time.time() * 1000),  # milliseconds
            )

        with self.lock:
            self.jobs[job_id] = job

        # Start execution in background thread
        thread = threading.Thread(
            target=target_func,
            args=(job_id, test_request),
            daemon=True,
        )
        thread.start()

        self.logger.info(
            f"{'Test density' if target_func == self._execute_density_test else 'Test performance'} started for job {job_id}"
        )

        return job_id

    def test_performance(self, performance_request: PerformanceTestSpec) -> str:
        """Start a performance test and return the job ID."""
        return self._start_job(performance_request, self._execute_performance_test)

    def test_density(self, density_request: DensityTestSpec) -> str:
        """Start a density test and return the job ID."""
        return self._start_job(density_request, self._execute_density_test)

    def _execute_performance_test(
        self,
        job_id: str,
        performance_request: PerformanceTestSpec,
    ):
        """Execute the performance test in a background thread."""
        try:
            # Calculate total streams
            total_streams = sum(
                spec.streams for spec in performance_request.pipeline_performance_specs
            )

            if total_streams == 0:
                self._update_job_error(
                    job_id,
                    "At least one stream must be specified to run the pipeline.",
                )
                return

            # Build pipeline command from specs
            pipeline_command = pipeline_manager.build_pipeline_command(
                performance_request.pipeline_performance_specs
            )

            # Initialize PipelineRunner
            runner = PipelineRunner()

            # Store runner for this job
            with self.lock:
                self.runners[job_id] = runner

            # Run the pipeline
            results = runner.run(
                pipeline_command=pipeline_command,
                total_streams=total_streams,
            )

            # Update job with results
            with self.lock:
                if job_id in self.jobs:
                    job = self.jobs[job_id]

                    # Check if job was cancelled while running
                    if runner.is_cancelled():
                        self.logger.info(
                            f"Pipeline {job_id} was cancelled, updating state to ABORTED"
                        )
                        job.state = TestJobState.ABORTED
                        job.end_time = int(time.time() * 1000)
                        job.error_message = "Cancelled by user"
                    else:
                        # Normal completion
                        job.state = TestJobState.COMPLETED
                        job.end_time = int(time.time() * 1000)

                        if results is not None:
                            # Build streams distribution per pipeline
                            streams_per_pipeline = [
                                PipelinePerformanceSpec(
                                    name=spec.name,
                                    version=spec.version,
                                    streams=spec.streams,
                                )
                                for spec in performance_request.pipeline_performance_specs
                            ]

                            # Update performance metrics
                            job.total_fps = results.total_fps
                            job.per_stream_fps = results.per_stream_fps
                            job.total_streams = results.num_streams
                            job.streams_per_pipeline = streams_per_pipeline

                # Clean up runner after completion
                self.runners.pop(job_id, None)

        except Exception as e:
            # Clean up runner on error
            with self.lock:
                self.runners.pop(job_id, None)
            self._update_job_error(job_id, str(e))

    def _execute_density_test(
        self,
        job_id: str,
        density_request: DensityTestSpec,
    ):
        """Execute the density test in a background thread."""
        try:
            # Initialize Benchmark
            benchmark = Benchmark()

            # Store benchmark runner for this job
            with self.lock:
                self.runners[job_id] = benchmark

            # Run the benchmark
            results = benchmark.run(
                pipeline_benchmark_specs=density_request.pipeline_density_specs,
                fps_floor=density_request.fps_floor,
            )

            # Update job with results
            with self.lock:
                if job_id in self.jobs:
                    job = self.jobs[job_id]

                    # Check if job was cancelled while running
                    if benchmark.runner.is_cancelled():
                        self.logger.info(
                            f"Density test {job_id} was cancelled, updating state to ABORTED"
                        )
                        job.state = TestJobState.ABORTED
                        job.end_time = int(time.time() * 1000)
                        job.error_message = "Cancelled by user"
                    else:
                        # Normal completion
                        job.state = TestJobState.COMPLETED
                        job.end_time = int(time.time() * 1000)

                        job.total_fps = None
                        job.per_stream_fps = results.per_stream_fps
                        job.streams_per_pipeline = results.streams_per_pipeline
                        job.total_streams = results.n_streams

                        self.logger.info(
                            f"Density test completed for job {job_id}: streams={results.n_streams}, streams_per_pipeline={results.streams_per_pipeline}, fps={results.per_stream_fps}"
                        )

                # Clean up benchmark after completion
                self.runners.pop(job_id, None)

        except Exception as e:
            # Clean up benchmark on error
            with self.lock:
                self.runners.pop(job_id, None)
            self._update_job_error(job_id, str(e))

    def _update_job_error(self, job_id: str, error_message: str):
        """Update job with error state."""
        with self.lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                job.state = TestJobState.ERROR
                job.end_time = int(time.time() * 1000)
                job.error_message = error_message
        self.logger.error(f"Pipeline test {job_id} error: {error_message}")

    def _build_performance_status(self, job: PerformanceJob) -> PerformanceJobStatus:
        """Helper to build PerformanceJobStatus from a PerformanceJob."""
        current_time = int(time.time() * 1000)
        elapsed_time = (
            job.end_time - job.start_time
            if job.end_time
            else current_time - job.start_time
        )
        return PerformanceJobStatus(
            id=job.id,
            start_time=job.start_time,
            elapsed_time=elapsed_time,
            state=job.state,
            total_fps=job.total_fps,
            per_stream_fps=job.per_stream_fps,
            total_streams=job.total_streams,
            streams_per_pipeline=job.streams_per_pipeline,
            error_message=job.error_message,
        )

    def _build_density_status(self, job: DensityJob) -> DensityJobStatus:
        """Helper to build DensityJobStatus from a DensityJob."""
        current_time = int(time.time() * 1000)
        elapsed_time = (
            job.end_time - job.start_time
            if job.end_time
            else current_time - job.start_time
        )
        return DensityJobStatus(
            id=job.id,
            start_time=job.start_time,
            elapsed_time=elapsed_time,
            state=job.state,
            total_fps=job.total_fps,
            per_stream_fps=job.per_stream_fps,
            total_streams=job.total_streams,
            streams_per_pipeline=job.streams_per_pipeline,
            error_message=job.error_message,
        )

    def get_job_statuses_by_type(self, job_type) -> list[TestsJobStatus]:
        """Get status of all jobs of a specific type (PerformanceJob or DensityJob).
        Returns a list of TestsJobStatus objects (common base for all job statuses).
        """
        with self.lock:
            statuses: list[TestsJobStatus] = []
            for job in self.jobs.values():
                if job_type == PerformanceJob and isinstance(job, PerformanceJob):
                    statuses.append(self._build_performance_status(job))
                elif job_type == DensityJob and isinstance(job, DensityJob):
                    statuses.append(self._build_density_status(job))
            self.logger.debug(f"Current job statuses for type {job_type}: {statuses}")
            return statuses

    def get_job_status(self, job_id: str) -> Optional[TestsJobStatus]:
        """Get status of a specific job by ID. Returns a TestsJobStatus object."""
        with self.lock:
            if job_id not in self.jobs:
                return None
            job = self.jobs[job_id]
            if isinstance(job, PerformanceJob):
                job_status = self._build_performance_status(job)
            elif isinstance(job, DensityJob):
                job_status = self._build_density_status(job)
            else:
                job_status = None
            self.logger.debug(f"Pipeline job status for {job_id}: {job_status}")
            return job_status

    def get_job_summary(
        self, job_id: str
    ) -> Optional[PerformanceJobSummary | DensityJobSummary]:
        """Get summary of a specific job."""
        with self.lock:
            if job_id not in self.jobs:
                return None

            job = self.jobs[job_id]

            if isinstance(job, PerformanceJob):
                job_summary = PerformanceJobSummary(
                    id=job.id,
                    request=job.request,
                )
            else:  # DensityJob
                job_summary = DensityJobSummary(
                    id=job.id,
                    request=job.request,
                )

            self.logger.debug(f"Pipeline job summary for {job_id}: {job_summary}")

            return job_summary

    def stop_job(self, job_id: str) -> tuple[bool, str]:
        """Stop a running pipeline job by calling cancel on its runner. Returns (success, message)."""
        with self.lock:
            if job_id not in self.jobs:
                msg = f"Job {job_id} not found"
                self.logger.warning(msg)
                return False, msg

            if job_id not in self.runners:
                msg = f"No active runner found for job {job_id}. It may have already completed or was never started."
                self.logger.warning(msg)
                return False, msg

            job = self.jobs[job_id]

            if job.state != TestJobState.RUNNING:
                msg = f"Job {job_id} is not running (state: {job.state})"
                self.logger.warning(msg)
                return False, msg

            runner = self.runners.get(job_id)
            if runner is None:
                msg = f"No active runner found for job {job_id}"
                self.logger.warning(msg)
                return False, msg

        runner.cancel()
        msg = f"Job {job_id} stopped"
        self.logger.info(msg)
        return True, msg
