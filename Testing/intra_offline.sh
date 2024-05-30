#!/bin/bash

idp_files=("mapcoloring.idp" "nqueen.idp" "testcase2.idp")
methods=("Offline" "Single" "Complete" "Kmedoids")
results_file="../Results/intra_offline_results.txt"
n_values=("3" "4" "6")

timeout_duration=300

cleanup() {
  echo "Script interrupted. Exiting..."
  exit 1
}

# Trap the interrupt signal (SIGINT)
trap cleanup SIGINT

# Function to run the Python script with a timeout
run_with_timeout() {
  local idp_file=$1
  local method=$2
  local n=$3
  local k_value=$4

  # Log the command being executed
  echo "Executing: python3 ../Diversity/diversity.py ../Base_Offline/$idp_file -n \"$n\" -k \"$k_value\" \"$method\""

  # Execute the Python script and capture the output
  output=$(timeout $timeout_duration python3 ../Diversity/diversity.py ../Base_Offline/$idp_file -n "$n" -k "$k_value" "$method")
  local exit_status=$?

  if [ $exit_status -eq 124 ]; then
    echo "Execution of k=$k_value took longer than $timeout_duration seconds. Stopping the script."
    return 1
  fi

  # Check if the output contains "No models."
  if [[ "$output" == *"No models."* || "$output" == *"Solution is not satisfiable"* ]]; then
    echo "No models found for k=$k_value."
    return 1
  fi

  return 0
}

# Initialize or clear the results file
> $results_file

# Loop through each IDP file
for idp_file in "${idp_files[@]}"; do
  # Loop through each method
  for method in "${methods[@]}"; do
    echo "Method: $method" >> $results_file
    echo '' >> $results_file

    # Loop through each n value
    for n in "${n_values[@]}"; do
      k=20
      while true; do
        echo "Running with k=$k for $idp_file, method=$method, n=$n"
        if ! run_with_timeout $idp_file $method $n $k; then
          # Record the last successful k value
          echo "$idp_file - $method - n=$n: Maximal k=$((k - 1))" >> $results_file
          echo "\hline" >> $results_file
          break
        fi
        # Increment k for the next iteration
        k=$((k + 1))
      done
    done
  done
done

echo "Completed all iterations."
