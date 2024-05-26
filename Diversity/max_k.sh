#!/bin/bash

# Initial value of k
k=12

# Maximum number of iterations (you can adjust this as needed)
max_iterations=100

# Timeout duration in seconds (5 minutes = 300 seconds)
timeout_duration=300

# Function to handle the script interruption
cleanup() {
  echo "Script interrupted. Exiting..."
  exit 1
}

# Trap the interrupt signal (SIGINT)
trap cleanup SIGINT

# Function to run the Python script with a timeout
run_with_timeout() {
  local k_value=$1
  local output
  # Capture the output of the Python script
  output=$(timeout $timeout_duration python3 diversity.py ../Base/testcase2.idp -n "3" -k "$k_value" "Offline")
  local exit_status=$?

  if [ $exit_status -eq 124 ]; then
    echo "Execution of k=$k_value took longer than $timeout_duration seconds. Stopping the script."
    exit 1
  fi

  # Check if the output contains "No models."
  if [[ "$output" == *"No models."* ]]; then
    echo "No models found for k=$k_value. Stopping the script."
    exit 1
  fi
}

# Loop to run the script with incrementing k values
for ((i=0; i<$max_iterations; i++)); do
  echo "Running with k=$k"
  run_with_timeout $k

  # Increment k for the next iteration
  k=$((k + 1))
done

echo "Completed all iterations."
