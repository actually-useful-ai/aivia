#!/bin/bash
# PyPI Upload Script for llamaball

set -e

# Extract version from __init__.py
VERSION=$(grep -o '__version__ = "[^"]*"' llamaball/__init__.py | cut -d'"' -f2)

echo "🦙 Llamaball PyPI Upload"
echo "======================="

# Check if dist files exist
if [ ! -f "dist/llamaball-$VERSION-py3-none-any.whl" ] || [ ! -f "dist/llamaball-$VERSION.tar.gz" ]; then
    echo "❌ Error: Distribution files not found. Run 'python -m build' first."
    exit 1
fi

echo "📦 Found distribution files:"
ls -la dist/llamaball-$VERSION*

echo ""
echo "🔑 PyPI Authentication"
echo "====================="
echo "Please enter your PyPI API token (starts with 'pypi-'):"
echo "You can get this from: https://pypi.org/manage/account/token/"
echo ""

# Read the API token securely
read -s -p "API Token: " PYPI_TOKEN
echo ""

if [[ ! $PYPI_TOKEN =~ ^pypi- ]]; then
    echo "❌ Error: Invalid token format. Token should start with 'pypi-'"
    exit 1
fi

echo "✅ Token format looks correct"

# Create temporary .pypirc file
PYPIRC_FILE=$(mktemp)
cat > "$PYPIRC_FILE" << EOF
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = $PYPI_TOKEN
EOF

echo ""
echo "🚀 Uploading to PyPI..."

# Upload using the temporary .pypirc file
python -m twine upload --config-file "$PYPIRC_FILE" dist/llamaball-$VERSION*

# Clean up
rm -f "$PYPIRC_FILE"

echo ""
echo "🎉 Upload complete!"
echo "🔗 View your package at: https://pypi.org/project/llamaball/"
echo "📦 Install with: pip install llamaball" 