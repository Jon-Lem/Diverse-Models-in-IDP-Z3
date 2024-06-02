#!/bin/bash

idp_files=("mapcoloring.idp" "nqueen.idp" "testcase2.idp")

declare -A nk_values=(
    ["mapcoloring.idp"]="3,117 4,234 6,475"
    ["nqueen.idp"]="3,36 4,72 6,180"
    ["testcase2.idp"]="3,29 4,58 6,141"
)

k_percent=("0.6" "0.8" "0.9" "1")

start_time=$(date +%s)

methods=("PyOffline")

results_file="../Results/pyoffline_speed.txt"
echo "Execution Results:" > $results_file

for idp_file in "${idp_files[@]}"; do
    nk_values_idp=(${nk_values[$idp_file]})
    
    # Write the program name
    program_name="${idp_file%.idp}"
    echo "\\begin{table}[htbp]" >> $results_file
    echo "  \\centering" >> $results_file
    echo "  \\begin{tabular}{|c||c|c|c|c|}" >> $results_file
    echo "    \\hline" >> $results_file
    echo "    \\multicolumn{5}{|c|}{Program: ${program_name^}} \\\\" >> $results_file
    echo "    \\hline" >> $results_file

    for nk in "${nk_values_idp[@]}"; do
        IFS=',' read -r n k <<< "$nk"

        echo "    \\multicolumn{1}{|c||}{} & \\multicolumn{4}{|c|}{n=$n} \\\\" >> $results_file
        echo "    \\hline" >> $results_file
        echo "    Method & 60\\% k & 80\\% k & 90\\% k & k (=$k) \\\\" >> $results_file
        echo "    \\hline" >> $results_file

        for method in "${methods[@]}"; do
            echo -n "    $method" >> $results_file

            for perc in "${k_percent[@]}"; do
                actual_k=$(echo "$k * $perc" | bc)

                # Log the command being executed
                echo "Executing: python3 ../Diversity/diversity.py ../Base_Offline/$idp_file -n \"$n\" -k \"$actual_k\" \"$method\""

                # Execute the Python script and capture the output
                output=$(python3 ../Diversity/diversity.py ../Base_Offline/$idp_file -n "$n" -k "$actual_k" "$method")

                # Extract execution time from the output
                time=$(echo "$output" | grep -o '[0-9]\+\.[0-9]\+ seconds')

                # Append results to the results file
                echo -n " & ${time:-X}" >> $results_file
            done

            echo " \\\\" >> $results_file
            echo "    \\cline{1-5}" >> $results_file
        done

        echo "    \\hline" >> $results_file
    done

    echo "  \\end{tabular}" >> $results_file
    echo "  \\caption{Performance of various methods for ${program_name^} problem}" >> $results_file
    echo "  \\label{tab:${program_name}}" >> $results_file
    echo "\\end{table}" >> $results_file
    echo "" >> $results_file
done

end_time=$(date +%s)
runtime=$((end_time - start_time))

echo "Total execution time: $runtime seconds"
