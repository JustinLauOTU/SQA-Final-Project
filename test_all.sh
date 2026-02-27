#!/bin/bash
#
# test_all.sh - Master test script
# Runs all tests and validates them in one command
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "======================================"
echo "Running CSCI 3060U Phase 3 Test Suite"
echo "======================================"
echo ""

# Step 1: Run all tests
echo "Step 1: Running tests..."
"$SCRIPT_DIR/run_tests.sh"

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Test execution failed"
    exit 1
fi

echo ""
echo "======================================"
echo ""

# Step 2: Validate results
echo "Step 2: Validating test results..."
"$SCRIPT_DIR/validate_tests.sh"

if [ $? -ne 0 ]; then
    echo ""
    echo "Some tests failed validation. Please review the failure log."
    echo "Document failures in failure_log.md"
    exit 1
fi

echo ""
echo "======================================"
echo "All tests passed!"
echo "======================================"
