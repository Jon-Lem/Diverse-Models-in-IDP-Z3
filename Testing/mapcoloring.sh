#!/bin/bash

idp_files=("mapcoloring.idp")

declare -A nk_values=(
    ["mapcoloring.idp"]="6,502"
)

k_percent=("0.6" "0.8" "0.9" "1")

start_time=$(date +%s)

methods=("Online1" "Online2" "Complete" "Kmedoids")

results_file="../Results/mapcoloring_n6_results.txt"
echo "\\multicolumn{1}{|c||}{} & \\multicolumn{4}{|c|}{n=6} \\\\" > $results_file
echo "\\hline" >> $results_file
echo "Method & 60\\% k & 80\\% k & 90\\% k & k (=502)\\\\" >> $results_file
echo "\\hline" >> $results_file

for idp_file in "${idp_files[@]}"; do
    nk_values_idp=(${nk_values[$idp_file]})

    for method in "${methods[@]}"; do
        echo -n "$method" >> $results_file

        if [[ "$method" == "Online1" || "$method" == "Online2" ]]; then
            base_directory="../Base_Online"
        else
            base_directory="../Base_Offline"
        fi

        for nk in "${nk_values_idp[@]}"; do
            IFS=',' read -r n k <<< "$nk"

            for perc in "${k_percent[@]}"; do
                actual_k=$(echo "$k * $perc" | bc)

                echo "Executing: python3 ../Diversity/diversity.py $base_directory/$idp_file -n \"$n\" -k \"$actual_k\" \"$method\""

                output=$(python3 ../Diversity/diversity.py $base_directory/$idp_file -n "$n" -k "$actual_k" "$method")

                time=$(echo "$output" | grep -o '[0-9]\+\.[0-9]\+ seconds')

                if [ -z "$time" ]; then
                    time="X"
                else
                    time=$(echo $time | grep -o '[0-9]\+\.[0-9]\+')
                fi

                echo -n " & $time" >> $results_file
            done
        done

        echo " \\\\" >> $results_file
        echo "\\cline{1-5}" >> $results_file
    done
done

echo "\\hline" >> $results_file
