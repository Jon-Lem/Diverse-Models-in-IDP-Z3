#!/bin/bash


k=137
max_iterations=100
timeout_duration=300
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
  output=$(timeout $timeout_duration python3 diversity.py ../Base/testcase2.idp -n "6" -k "$k_value" "Online1")
  # output=$(timeout $timeout_duration python3 diversity.py ../Base/mapcoloring.idp -n "6" -k "$k_value" "Online1")
  # output=$(timeout $timeout_duration python3 diversity.py ../Base/nqueenv2.idp -n "6" -k "$k_value" "Clustering")
  # output=$(timeout $timeout_duration python3 diversity.py ../Base/nqueenv2.idp -n "6" -k "$k_value" "Kmedoids")
  local exit_status=$?

  if [ $exit_status -eq 124 ]; then
    echo "Execution of k=$k_value took longer than $timeout_duration seconds. Stopping the script."
    exit 1
  fi

  # Check if the output contains "No models."
  if [[ "$output" == *"No models."* || "$output" == *"Solution is not satisfiable"* ]]; then
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
