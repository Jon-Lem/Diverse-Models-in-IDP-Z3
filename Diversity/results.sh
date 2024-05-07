#!/bin/bash

start_time=$(date +%s)

idp_files=("mapcoloring.idp" "nqueenv2.idp")
methods=("Online1" "Online2" "Clustering")
nk_values=("3,117" "4,234" "6,475")
k_percent=("0.6" "0.8" "0.9" "1")


for idp_file in "${idp_files[@]}"; do
    output_file="../Results/${idp_file%.*}.txt"
    
    if [[ ! -f $output_file ]]; then
        echo "Results for $idp_file experiments:" > "$output_file"
    fi

    for nk in "${nk_values[@]}"; do
        IFS=',' read -r n k <<< "$nk"
        for method in "${methods[@]}"; do
            for perc in "${k_percent[@]}"; do
                actual_k=$(echo "$k * $perc" | bc)

                echo "Executing: python3 diversity.py ../Base/$idp_file -n \"$n\" -k \"$actual_k\" \"$method\""
                output=$(python3 diversity.py ../Base/$idp_file -n "$n" -k "$actual_k" "$method")

                time=$(echo "$output" | grep -o '[0-9]\+\.[0-9]\+ seconds')

                echo "Time: ${time:-Not Available} seconds" >> "$output_file"
                echo "n: $n" >> "$output_file"
                echo "k: $k" >> "$output_file"
                echo "Method: $method" >> "$output_file"

                echo "=============================="
            done
        done
    done
done

# Record the end time
end_time=$(date +%s)

# Calculate the duration
duration=$((end_time - start_time))

# Print the total time taken
echo "Total execution time: $duration seconds"
