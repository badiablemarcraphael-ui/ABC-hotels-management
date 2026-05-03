"""
Grand Hotel Management System — Application Entry Point
Usage: python run.py
"""

import socket
import sys
import os

# Add the application directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app


def find_free_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    
    # If no port found in range, let OS assign one
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


if __name__ == '__main__':
    app = create_app()
    
    port = find_free_port(start_port=5000)
    
    print(f"""
╔══════════════════════════════════════════════════════╗
║          🏨 GRAND HOTEL MANAGEMENT SYSTEM            ║
║              Luxury Hospitality Suite                 ║
╠══════════════════════════════════════════════════════╣
║  Server starting on: http://127.0.0.1:{port}          ║
║  Environment: {'Development' if app.debug else 'Production'}                         ║
╚══════════════════════════════════════════════════════╝
    """)
    
    app.run(
        debug=True,
        port=port,
        host='127.0.0.1',
        threaded=True
    )