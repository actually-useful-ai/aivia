#!/bin/bash
# Comprehensive Build and Release Script for llamaball
# File Purpose: Build and release to PyPI and prepare conda recipe
# Primary Functions: Build package, upload to PyPI, create conda recipe
# Inputs: User confirmation and PyPI token
# Outputs: Published package and conda recipe

set -e

# Extract version from __init__.py
VERSION=$(grep -o '__version__ = "[^"]*"' llamaball/__init__.py | cut -d'"' -f2)

echo "🦙 Llamaball v$VERSION Build & Release"
echo "======================================"

# Step 1: Clean and build
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

echo "🔨 Building package..."
python -m build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Package built successfully"

# Step 2: Show what was built
echo ""
echo "📦 Built packages:"
ls -la dist/llamaball-$VERSION*

# Step 3: PyPI Upload
echo ""
echo "🚀 PyPI Upload"
echo "=============="
read -p "Upload to PyPI? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Please enter your PyPI API token (starts with 'pypi-'):"
    echo "Get it from: https://pypi.org/manage/account/token/"
    read -s -p "API Token: " PYPI_TOKEN
    echo ""
    
    if [[ ! $PYPI_TOKEN =~ ^pypi- ]]; then
        echo "❌ Error: Invalid token format. Token should start with 'pypi-'"
        exit 1
    fi
    
    echo "✅ Token format looks correct"
    echo "📤 Uploading to PyPI..."
    
    # Upload wheel
    echo "📦 Uploading wheel..."
    curl -s -X POST https://upload.pypi.org/legacy/ \
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
    curl -s -X POST https://upload.pypi.org/legacy/ \
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
        echo "🎉 PyPI upload complete!"
        echo "🔗 View at: https://pypi.org/project/llamaball/"
        echo "📦 Install with: pip install llamaball"
    else
        echo "❌ Failed to upload source distribution"
        exit 1
    fi
else
    echo "⏭️  Skipping PyPI upload"
fi

# Step 4: Conda Recipe
echo ""
echo "🐍 Conda Recipe"
echo "==============="

# Get SHA256 for conda recipe
SHA256=$(sha256sum dist/llamaball-$VERSION.tar.gz | cut -d' ' -f1)

# Update conda recipe with current version and hash
sed -i "s/{% set version = \".*\" %}/{% set version = \"$VERSION\" %}/" conda-recipe/meta.yaml
sed -i "s/sha256: .*/sha256: $SHA256/" conda-recipe/meta.yaml

echo "✅ Conda recipe updated with:"
echo "   Version: $VERSION"
echo "   SHA256: $SHA256"

echo ""
echo "📁 Conda recipe files:"
ls -la conda-recipe/

echo ""
echo "🔨 To build conda package locally:"
echo "   conda-build conda-recipe/"
echo ""
echo "📤 To submit to conda-forge:"
echo "   1. Fork https://github.com/conda-forge/staged-recipes"
echo "   2. Copy conda-recipe/ to recipes/llamaball/"
echo "   3. Submit pull request"

# Step 5: Summary
echo ""
echo "🎉 Build & Release Complete!"
echo "============================"
echo ""
echo "📋 Summary:"
echo "  ✅ Package v$VERSION built successfully"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  ✅ Uploaded to PyPI"
fi
echo "  ✅ Conda recipe prepared"
echo ""
echo "🔗 Next steps:"
echo "  1. Verify PyPI package: https://pypi.org/project/llamaball/"
echo "  2. Test installation: pip install llamaball==$VERSION"
echo "  3. Submit to conda-forge (optional)"
echo "  4. Create GitHub release with dist/ files"
echo ""
echo "🦙 Happy releasing!" 