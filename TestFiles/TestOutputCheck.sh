#!/bin/bash
# TestOutputCheck.sh - Validates test outputs against expected results
# This script compares actual outputs (.out and .atf files) with expected outputs
# for each test case found in subfolders.

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Counters
total_tests=0
passed_tests=0
failed_tests=0
missing_expected=0

echo "Validating Test Outputs"
echo "================================"

# Loop over all subdirectories in the script's folder
for test_folder in "$SCRIPT_DIR"/*/; do
    [ -d "$test_folder" ] || continue
    folder_name=$(basename "$test_folder")
    cd "$test_folder"

    # Process each *-INPUT.txt file in current folder
    for input_file in *-INPUT.txt; do
        [ -f "$input_file" ] || continue
        base=${input_file%-INPUT.txt}
        total_tests=$((total_tests + 1))

        echo "Test: $folder_name/$base"

        # ----- Validate terminal output (.out) -----
        actual_out="TestOutputs/$base.out"
        expected_out="$base-output.txt"

        if [ ! -f "$actual_out" ]; then
            echo -e "  ${RED}✗ Missing actual terminal output${NC}"
            failed_tests=$((failed_tests + 1))
        else
            if [ ! -f "$expected_out" ]; then
                echo -e "  ${YELLOW}⚠ Missing expected terminal output${NC}"
                missing_expected=$((missing_expected + 1))
            else
                if diff -u "$actual_out" "$expected_out" > /dev/null 2>&1; then
                    echo -e "  ${GREEN}✓ Terminal output matches${NC}"
                else
                    echo -e "  ${RED}✗ Terminal output differs${NC}"
                    echo "    Run: diff -u $actual_out $expected_out"
                    failed_tests=$((failed_tests + 1))
                fi
            fi
        fi

        # ----- Validate transaction file (.atf) -----
        actual_atf="TestOutputs/$base.atf"
        # Expected transaction file now uses .atf extension (instead of -atf.txt)
        expected_atf="$base.atf"

        if [ ! -f "$actual_atf" ]; then
            echo -e "  ${RED}✗ Missing actual transaction file${NC}"
            failed_tests=$((failed_tests + 1))
        else
            if [ ! -f "$expected_atf" ]; then
                echo -e "  ${YELLOW}⚠ Missing expected transaction file${NC}"
                missing_expected=$((missing_expected + 1))
            else
                if diff -u "$actual_atf" "$expected_atf" > /dev/null 2>&1; then
                    echo -e "  ${GREEN}✓ Transaction file matches${NC}"
                else
                    echo -e "  ${RED}✗ Transaction file differs${NC}"
                    echo "    Run: diff -u $actual_atf $expected_atf"
                    failed_tests=$((failed_tests + 1))
                fi
            fi
        fi

        echo ""   # blank line between tests
    done

    # Return to original script dir before processing next subfolder
    cd "$SCRIPT_DIR"
done

# Recalculate passed tests (tests with no failures and no missing expected files)
passed_tests=$((total_tests - failed_tests - missing_expected))
if [ $passed_tests -lt 0 ]; then
    passed_tests=0
fi

# Summary
echo "================================"
echo "Validation Summary:"
echo "  Total tests:    $total_tests"
echo -e "  ${GREEN}Passed:         $passed_tests${NC}"
echo -e "  ${RED}Failed:         $failed_tests${NC}"
echo -e "  ${YELLOW}Missing expected: $missing_expected${NC}"

if [ $missing_expected -gt 0 ]; then
    echo ""
    echo "To create expected outputs:"
    echo "  1. Review the actual outputs in the TestOutputs/ subfolders."
    echo "  2. If they are correct, copy them to the test folder with the proper names."
    echo "  Example: cp deposit/TestOutputs/DEP-01.out deposit/DEP-01-output.txt"
    echo "           cp deposit/TestOutputs/DEP-01.atf deposit/DEP-01.atf"
fi

# Exit with error if there were failures
if [ $failed_tests -gt 0 ]; then
    exit 1
else
    exit 0
fi