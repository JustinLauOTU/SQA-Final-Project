#!/bin/bash
# TestOutputCheck.sh - validates test outputs
# The follow script will:
#   1. Loop through each transaction subfolder (e.g. withdrawal, deposit, ect.)
#   2. For each *-INPUT.txt file in the folder, compares the generated .out and .atf (from TestOutput) files with the
#      expected output files
#   3. Reports pass/fail and shows differences if any

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Loop over all subdirectories in the script's folder
for i in "$SCRIPT_DIR"/*/; do
    [ -d "$i" ] || continue
    echo "Validating tests in folder $i"
    cd "$i"

    # Process each *-INPUT.txt file in current folder
    for x in *-INPUT.txt; do
        [ -f "$x" ] || continue
        base=${x%-INPUT.txt}
        # Validate terminal output
        if [ -f "TestOutputs/$base.out" ]; then
            if [ -f "$base-output.txt" ]; then
                # Compare expected vs actual using unified diff format
                if diff -u "$base-output.txt" "TestOutputs/$base.out"; then
                    echo "  $base.out OK"
                else
                    echo "  $base.out FAILED"
                fi
            else
                echo "  Missing expected output $base-output.txt"
            fi
        else
            echo "  Missing actual output TestOutputs/$base.out"
        fi

        # Validate transaction file
        if [ -f "TestOutputs/$base.atf" ]; then
            if [ -f "$base-atf.txt" ]; then
                if diff -u "$base-atf.txt" "TestOutputs/$base.atf"; then
                    echo "  $base.atf OK"
                else
                    echo "  $base.atf FAILED"
                fi
            else
                echo "  Missing expected atf $base-atf.txt"
            fi
        fi
    done

    # Return to original script dir before processing to next subfolder
    cd "$SCRIPT_DIR"
done