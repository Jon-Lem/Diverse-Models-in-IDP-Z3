#!/bin/bash

# List of IDP files to process
idp_files=("mapcoloring.idp" "nqueenv2.idp" "testcase2.idp")

# Declare an associative array for n, k values
declare -A nk_values=(
    ["mapcoloring.idp"]="3,117 4,234 6,475"
    ["nqueenv2.idp"]="3,36 4,72 6,180"
    ["testcase2.idp"]="3,29 4,58 6,141"
)

# k percentage multipliers
k_percent=("0.6" "0.8" "0.9" "1")

# Capture the start time
start_time=$(date +%s)

# List of methods to test
methods=("Offline" "Online1" "Online2" "Single" "Complete" "Kmedoids")

# Create results file
results_file="../Results/results.txt"
echo "Execution Results:" > $results_file

# Iterate over each IDP file
for idp_file in "${idp_files[@]}"; do
    nk_values_idp=(${nk_values[$idp_file]})

    # Loop through each method
    for method in "${methods[@]}"; do
        echo "Method: $method" >> $results_file
        echo '' >> $results_file

        # Loop through each n, k combination
        for nk in "${nk_values_idp[@]}"; do
            IFS=',' read -r n k <<< "$nk"

            # Loop through each k percentage multiplier
            for perc in "${k_percent[@]}"; do
                actual_k=$(echo "$k * $perc" | bc)

                # Log the command being executed
                echo "Executing: python3 diversity.py ../Base/$idp_file -n \"$n\" -k \"$actual_k\" \"$method\""

                # Execute the Python script and capture the output
                output=$(timeout 300 python3 diversity.py ../Base/$idp_file -n "$n" -k "$actual_k" "$method")
                if [[ $? -eq 124 ]]; then
                    # If timeout occurred, log 'Timeout'
                    time="Timeout"
                else
                    # Extract execution time from the output
                    time=$(echo "$output" | grep -o '[0-9]\+\.[0-9]\+ seconds')
                fi

                # Append results to the results file
                echo -n " & ${time:-X}" >> $results_file

                echo "=============================="
            done
        done
        echo "\hline" >> $results_file
    done
done

# Record the end time
end_time=$(date +%s)

# Calculate the total duration
duration=$((end_time - start_time))

# Print the total time taken
echo "Total execution time: $duration seconds"
