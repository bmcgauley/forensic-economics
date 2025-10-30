"""
Generate API Endpoints

Handles report generation requests and job status/download.
"""

from flask import Blueprint, request, jsonify, send_file
from src.models.intake import Intake, ValidationError
from src.jobs.manager import JobManager

# Create blueprint
generate_bp = Blueprint('generate', __name__)

# Global job manager instance
job_manager = JobManager()


@generate_bp.route('/generate', methods=['POST'])
def generate_report():
    """
    Generate a wrongful death economic loss report.

    Expects JSON body with intake data.
    Returns job_id and status_url for polling.
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate intake
        try:
            intake = Intake(data)
        except ValidationError as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400

        # Create job
        job_id = job_manager.create_job(intake.to_dict())

        # Return job info
        return jsonify({
            'job_id': job_id,
            'status_url': f'/api/status/{job_id}',
            'message': 'Report generation started'
        }), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@generate_bp.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """
    Get job status.

    Args:
        job_id: Job identifier from URL

    Returns:
        Job status including download URL when completed
    """
    status = job_manager.get_job_status(job_id)

    if not status:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify(status), 200


@generate_bp.route('/download/<job_id>', methods=['GET'])
def download_report(job_id):
    """
    Download completed report.

    Args:
        job_id: Job identifier from URL

    Returns:
        XLSX file download
    """
    result_file = job_manager.get_result_file(job_id)

    if not result_file:
        return jsonify({'error': 'Report not available'}), 404

    try:
        return send_file(
            result_file,
            as_attachment=True,
            download_name=result_file.name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'error': f'Failed to send file: {str(e)}'}), 500
