if [ $# -ne 3 ]; then
    echo "Usage: $0 gold_dir pipeline_outputs_dir output_dir"
    exit 1
fi

gold=$1
pipeline_outputs=$2
output=$3

if [ ! -d "$output" ]; then
    mkdir "$output"
fi

for testcase in $gold/*; do
    testcase_name=$(basename $testcase)
    echo "Checking $testcase_name"
    python3 pipeline_checker.py "$testcase" "$pipeline_outputs/$testcase_name" "$output/$testcase_name.csv"
done
