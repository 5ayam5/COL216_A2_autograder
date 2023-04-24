make BranchPredictorChecker

if [ $# -ne 3 ]; then
    echo "Usage: $0 predictions_dir testcases_dir output_dir"
    exit 1
fi

predictions=$1
testcases=$2
output=$3

if [ ! -d "$output" ]; then
    mkdir "$output"
fi

for testcase in "$predictions/*"; do
    testcase_name=$(basename $testcase)
    echo "Checking $testcase_name"
    ./BranchPredictorChecker "$testcase" "$testcases/$testcase_name" "$output/$testcase_name.csv"
done