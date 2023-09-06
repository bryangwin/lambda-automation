#!/bin/bash

# Description: This script will take the nvidia-bug-report.log.gz file from the Downloads directory,
# take the users input for the support ticket number related to the report, 
# apend the ticket number to the file name and store it in the nvidia_bug_reports directory
# You can use -o when you run the script to open the file with less after it's been moved

# Author: Bryan Gwin
# Date: 28 Aug 2023

# Change your source and target directories here:
SOURCE_DIR=~/Downloads
TARGET_DIR=~/nvidia_bug_reports

# Flag to determine if it should open the file with less
OPEN_WITH_LESS=false

# Parse command line options using getopts
OPTERR=0
INVALID_OPT="$1"

while getopts "o" opt; do
    case $opt in
        o)
            OPEN_WITH_LESS=true
            ;;
        \?)
            echo "Invalid option: $INVALID_OPT use -o if you'd like to open the file" >&2
            exit 1
            ;;
    esac
done

# Check if the target directory exists, if not, create it
if [[ ! -d "$TARGET_DIR" ]]; then
    mkdir "$TARGET_DIR"
fi

# Identify latest nvidia-bug-report.log.gz file in the source directory
latest_file=$(ls "$SOURCE_DIR"/nvidia-bug-report*.log.gz 2> /dev/null | sort -V | tail -n 1)

if [[ -f "$latest_file" ]]; then
    # Prompt the user for the ticket number
    echo -n "Enter the ticket number: "
    read ticket_number
    
    target_file="$TARGET_DIR"/nvidia-bug-report-${ticket_number}.log.gz

    # Check if target file exists, if it does, append with a version
    version=1
    while [[ -f "$target_file" || -f "${target_file%.gz}" ]]; do
        target_file="$TARGET_DIR"/nvidia-bug-report-${ticket_number}-v${version}.log.gz
        version=$((version+1))
    done
    
    mv "$latest_file" "$target_file"

    gunzip "$target_file"

    # Apply -o flag if user specified
    if $OPEN_WITH_LESS; then
        less "${target_file%.gz}"
    else
        echo "Success! $(basename "${target_file%.gz}") created in $TARGET_DIR"
    fi

else
    echo "Error: nvidia-bug-report.log.gz not found in $SOURCE_DIR"
fi
