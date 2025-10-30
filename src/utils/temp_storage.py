"""
Temporary Storage Utility

Purpose: Manage temporary file storage for job outputs and cleanup.
Creates temporary directories for job artifacts and provides cleanup policies.
"""

import os
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import threading


class TempStorage:
    """Manages temporary file storage for job outputs."""

    def __init__(self, base_path: Optional[str] = None, cleanup_hours: int = 24):
        """
        Initialize temporary storage manager.

        Args:
            base_path: Base directory for temp storage (defaults to system temp)
            cleanup_hours: Hours after which to clean up old job directories
        """
        if base_path:
            self.base_path = Path(base_path)
            self.base_path.mkdir(parents=True, exist_ok=True)
        else:
            self.base_path = Path(tempfile.gettempdir()) / 'forensic-economics'
            self.base_path.mkdir(parents=True, exist_ok=True)

        self.cleanup_hours = cleanup_hours
        self._lock = threading.Lock()

    def create_job_directory(self, job_id: str) -> Path:
        """
        Create a temporary directory for a job.

        Args:
            job_id: Unique job identifier

        Returns:
            Path to the created directory
        """
        with self._lock:
            job_dir = self.base_path / job_id
            job_dir.mkdir(parents=True, exist_ok=True)
            return job_dir

    def get_job_directory(self, job_id: str) -> Optional[Path]:
        """
        Get the directory path for a job.

        Args:
            job_id: Job identifier

        Returns:
            Path if it exists, None otherwise
        """
        job_dir = self.base_path / job_id
        return job_dir if job_dir.exists() else None

    def save_file(self, job_id: str, filename: str, content: bytes) -> Path:
        """
        Save a file to the job directory.

        Args:
            job_id: Job identifier
            filename: Name of the file
            content: File content as bytes

        Returns:
            Path to the saved file
        """
        job_dir = self.create_job_directory(job_id)
        file_path = job_dir / filename

        with open(file_path, 'wb') as f:
            f.write(content)

        return file_path

    def get_file_path(self, job_id: str, filename: str) -> Optional[Path]:
        """
        Get the path to a file in the job directory.

        Args:
            job_id: Job identifier
            filename: File name

        Returns:
            Path if the file exists, None otherwise
        """
        job_dir = self.get_job_directory(job_id)
        if not job_dir:
            return None

        file_path = job_dir / filename
        return file_path if file_path.exists() else None

    def cleanup_old_jobs(self) -> int:
        """
        Clean up job directories older than cleanup_hours.

        Returns:
            Number of directories cleaned up
        """
        if not self.base_path.exists():
            return 0

        cutoff_time = datetime.now() - timedelta(hours=self.cleanup_hours)
        cleaned_count = 0

        with self._lock:
            for job_dir in self.base_path.iterdir():
                if not job_dir.is_dir():
                    continue

                # Check directory modification time
                mtime = datetime.fromtimestamp(job_dir.stat().st_mtime)
                if mtime < cutoff_time:
                    try:
                        shutil.rmtree(job_dir)
                        cleaned_count += 1
                    except Exception as e:
                        print(f"Failed to clean up {job_dir}: {e}")

        return cleaned_count

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a specific job directory.

        Args:
            job_id: Job identifier

        Returns:
            True if deleted successfully, False otherwise
        """
        job_dir = self.get_job_directory(job_id)
        if not job_dir:
            return False

        with self._lock:
            try:
                shutil.rmtree(job_dir)
                return True
            except Exception:
                return False

    def get_storage_size(self) -> int:
        """
        Get total size of storage directory in bytes.

        Returns:
            Total size in bytes
        """
        if not self.base_path.exists():
            return 0

        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.base_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)

        return total_size
