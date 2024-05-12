#!/bin/bash


idp_files=("mapcoloring.idp" "nqueen.idp" "testcase2.idp")
# Define nk_values for each IDP file
declare -A nk_values=(
    ["mapcoloring.idp"]="3,117 4,234 6,475"
    ["nqueen.idp"]="3,36 4,48 6,72"
    ["testcase2.idp"]="3,29 4,58 6,141"
)
k_percent=("0.6" "0.8" "0.9" "1")

start_time=$(date +%s)

# Define the list of methods
methods=("Offline" "Online1" "Online2" "Clustering" "Kmedoids")

for idp_file in "${idp_files[@]}"; do
    num_model="${num_models[$i]}"
    nk_values_idp=(${nk_values[$idp_file]})

    # Loop through each combination of n, k, and method
    for method in "${methods[@]}"; do
        echo "Method: $method" >> ../Results/results.txt
        echo '' >> ../Results/results.txt
        for nk in "${nk_values_idp[@]}"; do
            IFS=',' read -r n k <<< "$nk"
            for perc in "${k_percent[@]}"; do
                actual_k=$(echo "$k * $perc" | bc)
                echo "Executing: python3 diversity.py ../Base/$idp_file -n \"$n\" -k \"$actual_k\" \"$method\""
                output=$(python3 diversity.py ../Base/$idp_file -n "$n" -k "$actual_k" "$method")
                time=$(echo "$output" | grep -o '[0-9]\+\.[0-9]\+ seconds')
                echo -n " & ${time:-Not Available}" >> ../Results/results.txt

                echo "=============================="
            done
        done
        echo "\hline" >> ../Results/results.txt
    done
done

# Record the end time
end_time=$(date +%s)

# Calculate the duration
duration=$((end_time - start_time))

# Print the total time taken
echo "Total execution time: $duration seconds"
