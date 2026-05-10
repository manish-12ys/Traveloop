#!/usr/bin/env python
"""
Traveloop Development Server

Run this file to start the Flask development server:
    python main.py

For production, use a WSGI server like Gunicorn:
    gunicorn wsgi:app
"""

import os
from app import create_app

# Create Flask app instance
app = create_app(os.getenv('FLASK_ENV', 'development'))


def main():
    """Run the Flask development server"""
    print("=" * 60)
    print(">> Starting Traveloop Flask Application")
    print("=" * 60)
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Debug Mode: {app.debug}")
    print()
    print("Available Routes:")
    print("  - Home: http://localhost:5000/")
    print("  - Health Check: http://localhost:5000/health")
    print()
    print("Press CTRL+C to quit")
    print("=" * 60)
    print()
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )


if __name__ == "__main__":
    main()

