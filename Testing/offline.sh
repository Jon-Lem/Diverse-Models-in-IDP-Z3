#!/bin/bash

# Check for the correct number of arguments
if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <n> <k> <idp_filename> <mode>"
  echo "mode should be either 'Single' or 'Complete'"
  exit 1
fi

n=$1
k=$2
idp_filename=$3
mode=$4
idp_file="../Base/$idp_filename"
max_iterations=100
timeout_duration=300

# Validate the mode
if [ "$mode" != "Single" ] && [ "$mode" != "Complete" ] && [ "$mode" != "Offline" ]; then
  echo "Invalid mode. Please pass 'Single' or 'Complete'."
  exit 1
fi

# Validate the IDP file
if [ ! -f "$idp_file" ]; then
  echo "The file $idp_file does not exist."
  exit 1
fi

cleanup() {
  echo "Script interrupted. Exiting..."
  echo "Last successful k value: $last_successful_k"
  exit 1
}

# Trap the interrupt signal (SIGINT)
trap cleanup SIGINT

# Function to run the Python script with a timeout
run_with_timeout() {
  local k_value=$1
  local output
  output=$(timeout $timeout_duration python3 diversity.py "$idp_file" -n "$n" -k "$k_value" "$mode")
  local exit_status=$?

  if [ $exit_status -eq 124 ]; then
    echo "Execution of k=$k_value took longer than $timeout_duration seconds. Stopping the script."
    echo "Last successful k value: $last_successful_k"
    exit 1
  fi

  # Check if the output contains "No models."
  if [[ "$output" == *"No models."* || "$output" == *"Solution is not satisfiable"* ]]; then
    echo "No models found for k=$k_value. Stopping the script."
    echo "Last successful k value: $last_successful_k"
    exit 1
  fi
}

# Initialize the last successful k value
last_successful_k=$k

# Loop to run the script with incrementing k values
for ((i=0; i<$max_iterations; i++)); do
  echo "Running with k=$k"
  run_with_timeout $k

  # Update the last successful k value
  last_successful_k=$k

  # Increment k for the next iteration
  k=$((k + 1))
done

echo "Completed all iterations."
echo "Last successful k value: $last_successful_k"
