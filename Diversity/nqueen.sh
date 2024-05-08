#!/bin/bash

start_time=$(date +%s)
methods=("Online1" "Online2" "Clustering")
nk_values=("3,36" "4,48" "6,72")
k_percent=("0.6" "0.8" "0.9" "1")


output_file="../Results/nqueen.txt"
if [[ ! -f $output_file ]]; then
    echo "Creating new output file..."
    echo "Results of nqueen experiments:" > "$output_file"
fi

for nk in "${nk_values[@]}"; do
    IFS=',' read -r n k <<< "$nk"
    for method in "${methods[@]}"; do
        for perc in "${k_percent[@]}"; do
            actual_k=$(echo "$k * $perc" | bc)

            echo "Executing: python3 diversity.py ../Base/nqueenv2.idp -n \"$n\" -k \"$actual_k\" \"$method\""
            output=$(python3 diversity.py ../Base/nqueenv2.idp -n "$n" -k "$actual_k" "$method")

            time=$(echo "$output" | grep -o '[0-9]\+\.[0-9]\+ seconds')

            # Write Results
            echo "Time: ${time:-Not Available} seconds" >> ../Results/nqueen.txt
            echo "n: $n" >> ../Results/nqueen.txt
            echo "k: $actual_k" >> ../Results/nqueen.txt
            echo "Method: $method" >> ../Results/nqueen.txt

            echo "=============================="
        done
    done
done


end_time=$(date +%s)
duration=$((end_time - start_time))

echo "Total execution time: $duration seconds"