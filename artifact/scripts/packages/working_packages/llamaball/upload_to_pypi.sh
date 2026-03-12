#!/bin/bash
# Simple PyPI Upload Script for llamaball
# File Purpose: Upload package to PyPI with token parameter
# Primary Functions: Upload wheel and source distribution to PyPI
# Inputs: PyPI token as parameter
# Outputs: Upload status and package URL

set -e

VERSION="1.1.1"
PYPI_TOKEN="$1"

if [ -z "$PYPI_TOKEN" ]; then
    echo "❌ Error: Please provide PyPI token as first argument"
    echo "Usage: $0 <pypi-token>"
    exit 1
fi

echo "🦙 Llamaball v$VERSION PyPI Upload"
echo "=================================="

# Check if dist files exist
WHEEL_FILE="dist/llamaball-$VERSION-py3-none-any.whl"
SDIST_FILE="dist/llamaball-$VERSION.tar.gz"

if [ ! -f "$WHEEL_FILE" ] || [ ! -f "$SDIST_FILE" ]; then
    echo "❌ Error: Distribution files not found. Run 'python -m build' first."
    exit 1
fi

echo "📦 Found distribution files:"
ls -la dist/llamaball-$VERSION*

echo ""
echo "🔐 Calculating checksums..."

# Calculate checksums for wheel
WHEEL_MD5=$(md5sum "$WHEEL_FILE" | cut -d' ' -f1)
WHEEL_SHA256=$(sha256sum "$WHEEL_FILE" | cut -d' ' -f1)

# Calculate checksums for sdist
SDIST_MD5=$(md5sum "$SDIST_FILE" | cut -d' ' -f1)
SDIST_SHA256=$(sha256sum "$SDIST_FILE" | cut -d' ' -f1)

echo "✅ Checksums calculated"

echo ""
echo "🚀 Uploading to PyPI..."

# Upload wheel file
echo "📦 Uploading wheel..."
WHEEL_RESPONSE=$(curl -s -w "%{http_code}" -X POST https://upload.pypi.org/legacy/ \
    -u "__token__:$PYPI_TOKEN" \
    -F ":action=file_upload" \
    -F "protocol_version=1" \
    -F "metadata_version=2.1" \
    -F "name=llamaball" \
    -F "version=$VERSION" \
    -F "summary=High-performance document chat and RAG system powered by Ollama" \
    -F "description=A local-first toolkit for document ingestion, embedding generation, and conversational AI interactions. Built for privacy and performance." \
    -F "author=Luke Steuber" \
    -F "author_email=luke@lukesteuber.com" \
    -F "license=MIT" \
    -F "home_page=https://github.com/coolhand/llamaball" \
    -F "classifier=Development Status :: 5 - Production/Stable" \
    -F "classifier=Environment :: Console" \
    -F "classifier=Intended Audience :: Developers" \
    -F "classifier=License :: OSI Approved :: MIT License" \
    -F "classifier=Programming Language :: Python :: 3" \
    -F "classifier=Programming Language :: Python :: 3.8" \
    -F "classifier=Programming Language :: Python :: 3.9" \
    -F "classifier=Programming Language :: Python :: 3.10" \
    -F "classifier=Programming Language :: Python :: 3.11" \
    -F "classifier=Programming Language :: Python :: 3.12" \
    -F "requires_python=>=3.8" \
    -F "filetype=bdist_wheel" \
    -F "pyversion=py3" \
    -F "md5_digest=$WHEEL_MD5" \
    -F "sha256_digest=$WHEEL_SHA256" \
    -F "content=@$WHEEL_FILE")

HTTP_CODE="${WHEEL_RESPONSE: -3}"
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Wheel uploaded successfully"
else
    echo "❌ Failed to upload wheel (HTTP $HTTP_CODE)"
    echo "Response: ${WHEEL_RESPONSE%???}"
    exit 1
fi

# Upload source distribution
echo "📦 Uploading source distribution..."
SDIST_RESPONSE=$(curl -s -w "%{http_code}" -X POST https://upload.pypi.org/legacy/ \
    -u "__token__:$PYPI_TOKEN" \
    -F ":action=file_upload" \
    -F "protocol_version=1" \
    -F "metadata_version=2.1" \
    -F "name=llamaball" \
    -F "version=$VERSION" \
    -F "summary=High-performance document chat and RAG system powered by Ollama" \
    -F "description=A local-first toolkit for document ingestion, embedding generation, and conversational AI interactions. Built for privacy and performance." \
    -F "author=Luke Steuber" \
    -F "author_email=luke@lukesteuber.com" \
    -F "license=MIT" \
    -F "home_page=https://github.com/coolhand/llamaball" \
    -F "classifier=Development Status :: 5 - Production/Stable" \
    -F "classifier=Environment :: Console" \
    -F "classifier=Intended Audience :: Developers" \
    -F "classifier=License :: OSI Approved :: MIT License" \
    -F "classifier=Programming Language :: Python :: 3" \
    -F "classifier=Programming Language :: Python :: 3.8" \
    -F "classifier=Programming Language :: Python :: 3.9" \
    -F "classifier=Programming Language :: Python :: 3.10" \
    -F "classifier=Programming Language :: Python :: 3.11" \
    -F "classifier=Programming Language :: Python :: 3.12" \
    -F "requires_python=>=3.8" \
    -F "filetype=sdist" \
    -F "pyversion=source" \
    -F "md5_digest=$SDIST_MD5" \
    -F "sha256_digest=$SDIST_SHA256" \
    -F "content=@$SDIST_FILE")

HTTP_CODE="${SDIST_RESPONSE: -3}"
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Source distribution uploaded successfully"
else
    echo "❌ Failed to upload source distribution (HTTP $HTTP_CODE)"
    echo "Response: ${SDIST_RESPONSE%???}"
    exit 1
fi

echo ""
echo "🎉 Upload complete!"
echo "🔗 View your package at: https://pypi.org/project/llamaball/"
echo "📦 Install with: pip install llamaball"
echo "🔄 It may take a few minutes for the package to be available" 