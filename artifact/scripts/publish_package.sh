#!/bin/bash
# Automated Package Publishing Pipeline
# Usage: ./publish_package.sh <package_name> [--test-only]
#
# Example: ./publish_package.sh fileherder
#          ./publish_package.sh fileherder --test-only

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Package directory base
PACKAGES_DIR="/home/coolhand/projects/packages/working"

# Functions
print_step() {
    echo -e "${GREEN}==>${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

print_error() {
    echo -e "${RED}Error:${NC} $1"
}

# Check arguments
if [ $# -lt 1 ]; then
    print_error "Usage: $0 <package_name> [--test-only]"
    echo ""
    echo "Available packages:"
    ls -1 "$PACKAGES_DIR"
    exit 1
fi

PACKAGE_NAME=$1
TEST_ONLY=false

if [ "$2" == "--test-only" ]; then
    TEST_ONLY=true
fi

PACKAGE_DIR="$PACKAGES_DIR/$PACKAGE_NAME"

# Verify package exists
if [ ! -d "$PACKAGE_DIR" ]; then
    print_error "Package directory not found: $PACKAGE_DIR"
    echo "Available packages:"
    ls -1 "$PACKAGES_DIR"
    exit 1
fi

print_step "Publishing $PACKAGE_NAME"
echo ""

# Navigate to package
cd "$PACKAGE_DIR"

# Step 1: Pre-flight checks
print_step "Step 1: Pre-flight checks"

# Check if build tools installed
if ! command -v python -m build &> /dev/null; then
    print_warning "build module not found. Installing..."
    pip install build twine
fi

# Check for pyproject.toml or setup.py
if [ ! -f "pyproject.toml" ] && [ ! -f "setup.py" ]; then
    print_error "No pyproject.toml or setup.py found"
    exit 1
fi

# Get current version
if [ -f "pyproject.toml" ]; then
    CURRENT_VERSION=$(grep "^version = " pyproject.toml | cut -d'"' -f2)
elif [ -f "setup.py" ]; then
    CURRENT_VERSION=$(grep "version=" setup.py | cut -d"'" -f2 | head -1)
fi

echo "Current version: $CURRENT_VERSION"
echo ""

# Step 2: Run tests (if they exist)
if [ -d "tests" ]; then
    print_step "Step 2: Running tests"
    pytest tests/ -v || {
        print_error "Tests failed! Fix tests before publishing."
        exit 1
    }
    echo ""
else
    print_warning "No tests directory found - skipping tests"
    echo ""
fi

# Step 3: Clean previous builds
print_step "Step 3: Cleaning previous builds"
rm -rf dist/ build/ *.egg-info/
echo "Build artifacts cleaned"
echo ""

# Step 4: Build package
print_step "Step 4: Building package"
python -m build
echo ""

# Step 5: Check package
print_step "Step 5: Checking package quality"
twine check dist/*
echo ""

# List built files
echo "Built files:"
ls -lh dist/
echo ""

# Step 6: Upload to TestPyPI
print_step "Step 6: Uploading to TestPyPI"
twine upload --repository testpypi dist/* || {
    print_warning "TestPyPI upload failed (may be version conflict)"
}
echo ""

# Step 7: Test installation from TestPyPI
print_step "Step 7: Testing installation from TestPyPI"
echo "Waiting 30 seconds for TestPyPI to process..."
sleep 30

# Create temporary venv for testing
TEMP_VENV="/tmp/test_${PACKAGE_NAME}_install"
rm -rf "$TEMP_VENV"
python -m venv "$TEMP_VENV"
source "$TEMP_VENV/bin/activate"

pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    "$PACKAGE_NAME" || {
    print_error "Installation from TestPyPI failed"
    deactivate
    rm -rf "$TEMP_VENV"
    exit 1
}

# Test import
python -c "import $PACKAGE_NAME; print('✅ Import successful')" || {
    print_error "Import test failed"
    deactivate
    rm -rf "$TEMP_VENV"
    exit 1
}

deactivate
rm -rf "$TEMP_VENV"
echo ""

# Step 8: Upload to Production PyPI (if not test-only)
if [ "$TEST_ONLY" = true ]; then
    print_step "Test-only mode - Skipping production PyPI upload"
    echo ""
    print_step "✅ Package ready for production!"
    echo "To publish to production PyPI, run:"
    echo "  cd $PACKAGE_DIR"
    echo "  twine upload dist/*"
else
    print_step "Step 8: Uploading to Production PyPI"
    echo ""
    read -p "Upload to PRODUCTION PyPI? This cannot be undone! (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        twine upload dist/*
        echo ""
        print_step "✅ Package published to PyPI!"
        echo ""
        echo "Verify at: https://pypi.org/project/$PACKAGE_NAME/"
        echo "Install with: pip install $PACKAGE_NAME"
    else
        echo "Cancelled. Package NOT uploaded to production PyPI."
        echo "To upload manually later:"
        echo "  cd $PACKAGE_DIR"
        echo "  twine upload dist/*"
    fi
fi

echo ""

# Step 9: Post-publication tasks
print_step "Step 9: Post-publication checklist"
echo ""
echo "Remember to:"
echo "  1. Tag release in git: git tag v$CURRENT_VERSION && git push origin v$CURRENT_VERSION"
echo "  2. Update README with PyPI badge"
echo "  3. Announce release (if appropriate)"
echo "  4. Monitor PyPI statistics"
echo "  5. Update CHANGELOG for next version"
echo ""

print_step "✨ Publication process complete!"
