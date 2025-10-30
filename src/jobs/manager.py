"""
Job Manager

Purpose: Queue jobs, track status, and manage temporary job folders.
Handles in-memory job tracking and orchestrates agent execution.
"""

import uuid
import threading
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import traceback

from src.utils.temp_storage import TempStorage
from src.agents.supervisor_agent import SupervisorAgent
from src.aggregator import Aggregator
from src.xlsx.xlsx_generator import XLSXGenerator


class JobStatus(Enum):
    """Job status enumeration."""
    QUEUED = 'queued'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'


class Job:
    """Represents a single report generation job."""

    def __init__(self, job_id: str, intake: Dict[str, Any]):
        """
        Initialize a job.

        Args:
            job_id: Unique job identifier
            intake: Intake data dictionary
        """
        self.job_id = job_id
        self.intake = intake
        self.status = JobStatus.QUEUED
        self.message = 'Job queued'
        self.error = None
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.result_file = None
        self.agent_results = []
        self.agent_progress = []
        self.current_step = ''
        self.progress_pct = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary."""
        return {
            'job_id': self.job_id,
            'status': self.status.value,
            'message': self.message,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result_file': self.result_file,
            'current_step': self.current_step,
            'progress_pct': self.progress_pct,
            'agent_progress': self.agent_progress
        }


class JobManager:
    """Manages job queue and execution."""

    def __init__(self, temp_storage: Optional[TempStorage] = None):
        """
        Initialize job manager.

        Args:
            temp_storage: TempStorage instance (optional, creates default if None)
        """
        self.jobs: Dict[str, Job] = {}
        self.temp_storage = temp_storage or TempStorage()
        self._lock = threading.Lock()

    def create_job(self, intake: Dict[str, Any]) -> str:
        """
        Create a new job.

        Args:
            intake: Validated intake data

        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        job = Job(job_id, intake)

        with self._lock:
            self.jobs[job_id] = job

        # Start job execution in background thread
        thread = threading.Thread(target=self._execute_job, args=(job_id,))
        thread.daemon = True
        thread.start()

        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job object if found, None otherwise
        """
        with self._lock:
            return self.jobs.get(job_id)

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status.

        Args:
            job_id: Job identifier

        Returns:
            Job status dictionary if found, None otherwise
        """
        job = self.get_job(job_id)
        if not job:
            return None

        status = job.to_dict()

        # Add download URL if completed
        if job.status == JobStatus.COMPLETED and job.result_file:
            status['download_url'] = f'/api/download/{job_id}'
            status['filename'] = Path(job.result_file).name

        return status

    def _execute_job(self, job_id: str):
        """
        Execute a job (runs in background thread).

        Args:
            job_id: Job identifier
        """
        job = self.get_job(job_id)
        if not job:
            return

        try:
            # Update status
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            job.message = 'Initializing supervisor agent...'
            job.current_step = 'Starting analysis...'

            # Create job directory
            job_dir = self.temp_storage.create_job_directory(job_id)

            # Define progress callback to update job progress in real-time
            def progress_callback(agent_progress):
                """Update job progress when agent status changes."""
                job.current_step = agent_progress.message
                job.message = f'{agent_progress.name}: {agent_progress.message}'

                # Update agent progress list
                # Find existing progress entry or add new one
                found = False
                for i, existing in enumerate(job.agent_progress):
                    if existing.get('name') == agent_progress.name:
                        job.agent_progress[i] = agent_progress.to_dict()
                        found = True
                        break
                if not found:
                    job.agent_progress.append(agent_progress.to_dict())

                # Calculate overall progress percentage
                total_agents = 7
                completed = sum(1 for p in job.agent_progress if p.get('status') == 'COMPLETED')
                job.progress_pct = int((completed / total_agents) * 100)

            # Initialize Supervisor Agent with progress callback
            supervisor = SupervisorAgent(progress_callback=progress_callback)

            # Run all agents via Supervisor
            job.message = 'Running agents via Supervisor...'
            supervisor_result = supervisor.run(job.intake)

            # Extract agent results from supervisor output
            job.agent_results = supervisor_result['outputs']['agent_results']

            # Update progress from supervisor
            progress_data = supervisor.get_progress()
            job.current_step = progress_data['current_step']
            job.progress_pct = progress_data['progress_pct']
            job.agent_progress = progress_data['agents']

            # Aggregate results
            job.message = 'Aggregating results...'
            job.current_step = 'Aggregating agent outputs...'
            aggregator = Aggregator()
            final_workbook = aggregator.aggregate(job.agent_results, job.intake)

            # Generate XLSX
            job.message = 'Generating Excel workbook...'
            job.current_step = 'Creating Excel report...'
            xlsx_generator = XLSXGenerator()
            output_filename = f"wrongful_death_report_{job_id[:8]}.xlsx"
            output_path = str(job_dir / output_filename)
            xlsx_generator.generate(final_workbook, output_path)

            # Mark as completed
            job.status = JobStatus.COMPLETED
            job.message = 'Report generated successfully'
            job.current_step = 'Completed'
            job.progress_pct = 100
            job.completed_at = datetime.utcnow()
            job.result_file = output_path

        except Exception as e:
            # Mark as failed
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.message = f'Job failed: {str(e)}'
            job.current_step = 'Failed'
            job.completed_at = datetime.utcnow()

            # Log full traceback for debugging
            print(f"Job {job_id} failed:")
            traceback.print_exc()

    def get_result_file(self, job_id: str) -> Optional[Path]:
        """
        Get the result file path for a completed job.

        Args:
            job_id: Job identifier

        Returns:
            Path to result file if available, None otherwise
        """
        job = self.get_job(job_id)
        if not job or job.status != JobStatus.COMPLETED or not job.result_file:
            return None

        result_path = Path(job.result_file)
        return result_path if result_path.exists() else None

    def cleanup_old_jobs(self, hours: int = 24) -> int:
        """
        Clean up old jobs and their files.

        Args:
            hours: Age threshold in hours

        Returns:
            Number of jobs cleaned up
        """
        return self.temp_storage.cleanup_old_jobs()
