#!/bin/bash
# Install Web Dependencies for Llamaball
# File Purpose: Install Flask and web server dependencies
# Primary Functions: Package installation, dependency management
# Inputs: None
# Outputs: Installed packages

set -e

echo "🦙 Installing Llamaball Web Server Dependencies..."

# Install Flask and web dependencies
pip install flask flask-cors

# Optional: Install cryptography for SSL support
echo "📦 Installing optional SSL support..."
pip install cryptography

# Optional: Install production WSGI server
echo "🚀 Installing production server (Gunicorn)..."
pip install gunicorn

echo "✅ Web dependencies installed successfully!"
echo ""
echo "🚀 You can now start the web server with:"
echo "   python start_web_server.py"
echo ""
echo "🔐 For HTTPS (recommended for production):"
echo "   python start_web_server.py --https"
echo ""
echo "🌐 For production deployment:"
echo "   gunicorn -w 4 -b 0.0.0.0:8080 'llamaball.web_server:create_app()'" 