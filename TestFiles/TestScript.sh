#!/bin/bash
# TestScript.sh - Will run all test in subfolders
# The follow script will:
#   1. Loop through each transaction subfolder (e.g. withdrawal, deposit, ect.)
#   2. For each *-INPUT.txt file in the folder, it will run the banking system for that specific test
#   3. Save the terminal output to TestOutputs/<base>.out and transaction file to TestOutputs/<bas>.aft

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# BankSystem and current_bank_accounts file directory
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$PROJECT_ROOT/BankingSystem.py"
ACCOUNTS_FILE="$PROJECT_ROOT/current_bank_accounts.txt"

# Loop over each subdirectory (e.g. withdrawal, deposit, ect.)
for i in "$SCRIPT_DIR"/*/; do
    [ -d "$i" ] || continue             # Skip if not a directory (e.g. if no subfolders exist)
    echo "Running tests in folder $i"
    cd "$i"                             # Move into test folder

    # Create TestOutputs folder if missing
    mkdir -p TestOutputs

    # Loop for all files in the current folder with "-INPUT.txt"
    for x in *-INPUT.txt; do
        [ -f "$x" ] || continue         # Skip if not a directory (e.g. if no subfolders exist)
        echo "Running test $x"
        base=${x%-INPUT.txt}            # Extract base name of file (e.g. "CP" of "CP-01-INPUT.txt)

        # Run the banking system
        #   - Give program two file names (current_bank_account file and output transaction file path)
        #   - Give inputs from file as stdin
        #   - Send everything the program outputs into the specific .out file
        python3 "$PYTHON_SCRIPT" "$ACCOUNTS_FILE" "TestOutputs/$base.atf" < "$x" > "TestOutputs/$base.out" 2>&1
    done

    # Return to original script dir before processing to next subfolder
    cd "$SCRIPT_DIR"
done