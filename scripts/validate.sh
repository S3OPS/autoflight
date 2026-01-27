#!/bin/bash
#
# Validation script for autoflight installation
# Tests all major components to ensure proper setup
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Activate venv if it exists and not already activated
if [ -d ".venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    source .venv/bin/activate
fi

# Configuration
MIN_SAMPLE_IMAGES=3

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Autoflight Installation Validation${NC}"
echo "===================================="
echo ""

PASSED=0
FAILED=0

# Test 1: Check Python version
echo -n "Testing Python version... "
PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Failed"
    ((FAILED++))
fi

# Test 2: Check package imports
echo -n "Testing package imports... "
if python -c "import autoflight; import cv2; import numpy" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} All packages imported"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Failed to import packages"
    ((FAILED++))
fi

# Test 3: Run unit tests
echo -n "Testing unit tests... "
if python -m unittest discover -s tests -p "test_*.py" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} All tests passed"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Some tests failed"
    ((FAILED++))
fi

# Test 4: Check CLI command
echo -n "Testing CLI command... "
if autoflight --help > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} CLI command works"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} CLI command failed"
    ((FAILED++))
fi

# Test 5: Check sample images
echo -n "Testing sample images... "
if [ -d "sample_images" ] && [ "$(ls -A sample_images/*.jpg 2>/dev/null | wc -l)" -ge "$MIN_SAMPLE_IMAGES" ]; then
    echo -e "${GREEN}✓${NC} Sample images present"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Sample images missing"
    ((FAILED++))
fi

# Test 6: Test orthomosaic generation
echo -n "Testing orthomosaic generation... "
TEST_OUTPUT="/tmp/test_orthomosaic_$$.jpg"
if python -m autoflight.orthomosaic sample_images "$TEST_OUTPUT" > /dev/null 2>&1; then
    if [ -f "$TEST_OUTPUT" ]; then
        echo -e "${GREEN}✓${NC} Orthomosaic generated successfully"
        rm -f "$TEST_OUTPUT"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Output file not created"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗${NC} Generation failed"
    ((FAILED++))
fi

# Test 7: Check documentation
echo -n "Testing documentation... "
DOC_COUNT=0
[ -f "README.md" ] && ((DOC_COUNT++))
[ -f "QUICKSTART.md" ] && ((DOC_COUNT++))
[ -f "CONTRIBUTING.md" ] && ((DOC_COUNT++))
[ -f "CHANGELOG.md" ] && ((DOC_COUNT++))
[ -f "LICENSE" ] && ((DOC_COUNT++))

if [ $DOC_COUNT -ge 5 ]; then
    echo -e "${GREEN}✓${NC} All documentation present"
    ((PASSED++))
else
    echo -e "${YELLOW}!${NC} Some documentation missing ($DOC_COUNT/5)"
    ((PASSED++))
fi

# Summary
echo ""
echo "===================================="
echo -e "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
echo "===================================="
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All validation tests passed!${NC}"
    echo "Your autoflight installation is ready to use."
    exit 0
else
    echo -e "${RED}✗ Some validation tests failed.${NC}"
    echo "Please check the errors above and run ./bootstrap.sh again."
    exit 1
fi
