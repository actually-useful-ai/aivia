#!/bin/bash
# PyPI Upload Script using curl for llamaball

set -e

VERSION="1.1.1"

echo "🦙 Llamaball PyPI Upload (curl method)"
echo "======================================"

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

echo ""
echo "🚀 Uploading to PyPI..."

# Upload wheel file
echo "📦 Uploading wheel..."
curl -X POST https://upload.pypi.org/legacy/ \
    -u "__token__:$PYPI_TOKEN" \
    -F ":action=file_upload" \
    -F "protocol_version=1" \
    -F "name=llamaball" \
    -F "version=$VERSION" \
    -F "filetype=bdist_wheel" \
    -F "pyversion=py3" \
    -F "content=@dist/llamaball-$VERSION-py3-none-any.whl"

if [ $? -eq 0 ]; then
    echo "✅ Wheel uploaded successfully"
else
    echo "❌ Failed to upload wheel"
    exit 1
fi

# Upload source distribution
echo "📦 Uploading source distribution..."
curl -X POST https://upload.pypi.org/legacy/ \
    -u "__token__:$PYPI_TOKEN" \
    -F ":action=file_upload" \
    -F "protocol_version=1" \
    -F "name=llamaball" \
    -F "version=$VERSION" \
    -F "filetype=sdist" \
    -F "pyversion=source" \
    -F "content=@dist/llamaball-$VERSION.tar.gz"

if [ $? -eq 0 ]; then
    echo "✅ Source distribution uploaded successfully"
else
    echo "❌ Failed to upload source distribution"
    exit 1
fi

echo ""
echo "🎉 Upload complete!"
echo "🔗 View your package at: https://pypi.org/project/llamaball/"
echo "📦 Install with: pip install llamaball" 