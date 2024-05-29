#!/bin/bash


idp_files=("mapcoloring.idp" "nqueen.idp" "testcase2.idp")

declare -A nk_values=(
    ["mapcoloring.idp"]="3,117 4,234 6,475"
    ["nqueenv2.idp"]="3,36 4,72 6,180"
    ["testcase2.idp"]="3,29 4,58 6,141"
)

k_percent=("0.6" "0.8" "0.9" "1")

start_time=$(date +%s)

methods=("Online1" "Online2")

results_file="../Results/online_results.txt"
echo "Execution Results:" > $results_file

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
                echo "Executing: python3 ../Diversity/diversity.py ../Base_Online/$idp_file -n \"$n\" -k \"$actual_k\" \"$method\""

                # Execute the Python script and capture the output
                output=$(timeout 300 python3 ../Diversity/diversity.py ../Base_Online/$idp_file -n "$n" -k "$actual_k" "$method")
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