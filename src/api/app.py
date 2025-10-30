"""
Forensic Economics - Flask Application Factory

Minimal Flask app scaffold implementing app factory pattern and basic routing.
Serves the single-page dashboard and provides REST API endpoints for generating
wrongful death economic loss reports.
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
import os


def create_app(config=None):
    """
    Application factory function.

    Args:
        config: Optional configuration dictionary

    Returns:
        Flask application instance
    """
    app = Flask(__name__,
                static_folder='../../static',
                static_url_path='')

    # Enable CORS for development
    CORS(app)

    # Default configuration
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max request size
        'JSON_SORT_KEYS': False,
    })

    # Override with custom config if provided
    if config:
        app.config.update(config)

    # Register routes
    @app.route('/')
    def index():
        """Serve the main dashboard."""
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/health')
    def health():
        """Health check endpoint."""
        return {'status': 'ok', 'service': 'forensic-economics'}, 200

    # Register API blueprints
    from src.api.generate import generate_bp
    app.register_blueprint(generate_bp, url_prefix='/api')

    return app


def main():
    """Run the development server."""
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"Starting Forensic Economics server on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()
