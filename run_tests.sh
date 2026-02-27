#!/bin/bash
#
# run_tests.sh - Automated test script for Phase 3
# This script runs the banking system with each test input file
# and saves both terminal output and transaction files
#

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TESTS_DIR="$SCRIPT_DIR/tests"
INPUTS_DIR="$TESTS_DIR/inputs"
OUTPUTS_DIR="$TESTS_DIR/outputs"
ACCOUNTS_FILE="$SCRIPT_DIR/current_bank_accounts.txt"

# Clear previous outputs
echo "Cleaning previous test outputs..."
rm -f "$OUTPUTS_DIR"/*.out "$OUTPUTS_DIR"/*.atf

# Check if inputs directory exists
if [ ! -d "$INPUTS_DIR" ]; then
    echo -e "${RED}Error: Inputs directory not found at $INPUTS_DIR${NC}"
    exit 1
fi

# Check if accounts file exists
if [ ! -f "$ACCOUNTS_FILE" ]; then
    echo -e "${RED}Error: Accounts file not found at $ACCOUNTS_FILE${NC}"
    exit 1
fi

# Count total tests
total_tests=$(ls -1 "$INPUTS_DIR" | wc -l)
echo "Found $total_tests test(s) to run"
echo "================================"

# Loop through all test input files
test_count=0
for test_input in "$INPUTS_DIR"/*; do
    if [ -f "$test_input" ]; then
        test_name=$(basename "$test_input")
        test_count=$((test_count + 1))
        
        echo -e "${GREEN}[$test_count/$total_tests] Running test: $test_name${NC}"
        
        # Define output files
        output_log="$OUTPUTS_DIR/${test_name}.out"
        output_transaction="$OUTPUTS_DIR/${test_name}.atf"
        
        # Run the banking system
        # Input from test file, terminal output to .out file, transaction file to .atf
        cd "$SCRIPT_DIR"
        python3 BankingSystem.py "$ACCOUNTS_FILE" "$output_transaction" < "$test_input" > "$output_log" 2>&1
        
        # Check if test ran successfully
        if [ $? -eq 0 ]; then
            echo "  ✓ Test completed"
        else
            echo "  ✗ Test failed with exit code $?"
        fi
        
        # Show size of output files
        if [ -f "$output_log" ]; then
            log_size=$(wc -l < "$output_log")
            echo "  Terminal output: $log_size lines"
        fi
        
        if [ -f "$output_transaction" ]; then
            trans_size=$(wc -l < "$output_transaction")
            echo "  Transaction file: $trans_size lines"
        fi
        
        echo ""
    fi
done

echo "================================"
echo "Test run complete!"
echo "Results saved to: $OUTPUTS_DIR"
