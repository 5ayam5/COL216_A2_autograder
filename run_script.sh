if [ $# -ne 6 ]; then
    echo "Usage: $0 <submission_dir> <workspace> <testcases> <outputs> <pipeline_gold> <unpipelined_wd>"
    exit 1
fi

submission_dir=$1
workspace=$2
testcases=$3
outputs=$4
pipeline_gold=$5
unpipelined_wd=$6
wd=$(pwd)

if [ ! -d "$submission_dir" ]; then
    echo "Submission directory does not exist"
    exit 1
fi

if [ ! -d "$workspace" ]; then
    echo "Workspace directory does not exist"
    exit 1
fi

if [ ! -d "$testcases" ]; then
    echo "Testcases directory does not exist"
    exit 1
fi

if [ ! -d "$outputs" ]; then
    mkdir "$outputs"
fi

if [ ! -d "$pipeline_gold" ]; then
    echo "Pipeline gold directory does not exist"
    exit 1
fi

echo "Unzipping submissions"
echo > "$outputs/missing"
for student in "$submission_dir"/*; do
    if compgen -G "$student/*_*_A2.zip" > /dev/null; then
        unzip -o "$student/*_*_A2.zip" -d "$student" > /dev/null
    else
        echo "  Missing zip file for $student"
        echo "$student" >> "$outputs/missing"
    fi
done

echo "Running pipeline code"
if [ ! -d "$outputs/pipeline" ]; then
    mkdir "$outputs/pipeline"
fi
echo -n > "$outputs/pipeline_compile_error"

for student in "$submission_dir"/*; do
    student_name=$(basename "$(ls "$student"/*_*_A2.zip)")
    if [ ${#student_name} -ge 4 ]; then
        student_name=${student_name::-4}
    else
        continue
    fi
    if [ ! -d "$outputs/pipeline/$student_name" ]; then
        mkdir "$outputs/pipeline/$student_name"
    fi

    echo "  Running $student_name"
    log_file="$wd/$outputs/pipeline/$student_name/log"
    echo -n > "$log_file"

    (cd "$student/$student_name" > /dev/null 2>&1 && make -s compile >> "$log_file" 2>&1)
    success=$?
    if [ $success != 0 ]; then
        echo "$student_name" >> "$outputs/pipeline_compile_error"
    fi

    for testcase in "$testcases"/pipeline/*; do
        testcase_name=$(basename "$testcase")
        if [ ! -d "$outputs/pipeline/$student_name/$testcase_name" ]; then
            mkdir "$outputs/pipeline/$student_name/$testcase_name"
        fi

        if [ $success -eq 0 ]; then
            echo "Running $testcase_name" >> "$log_file"
            cp "$testcase" "$student/$student_name/input.asm"
            
            pushd "$student/$student_name" > /dev/null 2>&1
            timeout 60 make -s run_5stage > "$wd/$outputs/pipeline/$student_name/$testcase_name/5_nobypass" 2> "$log_file"
            timeout 60 make -s run_5stage_bypass > "$wd/$outputs/pipeline/$student_name/$testcase_name/5_bypass" 2> "$log_file"
            timeout 60 make -s run_79stage > "$wd/$outputs/pipeline/$student_name/$testcase_name/79_nobypass" 2> "$log_file"
            timeout 60 make -s run_79stage_bypass > "$wd/$outputs/pipeline/$student_name/$testcase_name/79_bypass" 2> "$log_file"
            popd > /dev/null 2>&1
        fi
    done
done
exit 0

echo "Running pipeline checker"
make -s -C "$unpipelined_wd" > /dev/null 2>&1
for testcase in "$testcases"/pipeline/*; do
    testcase_name=$(basename "$testcase")
    echo $testcase
    pushd "$unpipelined_wd" > /dev/null 2>&1
    ./sample  "$wd/$testcase" > "$wd/$pipeline_gold/$testcase_name/79"
    popd > /dev/null 2>&1
done
exit 0

./pipeline_checker.sh "$pipeline_gold" "$outputs/pipeline" "$outputs/pipeline_checker"
exit 0

echo "Running branch predictor code"
for testcase in "$testcases/branch_predictor/*"; do
    testcase_name=$(basename $testcase)
    echo "  Running $testcase_name"

    for student in "$submission_dir/*"; do
        student_name=$(basename "$(ls "$student"/*_*_A2.zip)")
        student_name=${student_name::-4}
        if [ ! -f "$student/$student_name/BranchPredictor.hpp" ]; then
            continue
        fi
        cp "$student/BranchPredictor.hpp" "$workspace/BranchPredictor.hpp"
        make -s -C "$workspace" BranchPredictor
        ./"$workspace/BranchPredictor" "$student_name" "$testcase" "$outputs/branch_predictor/$testcase_name"
    done
done

echo "Running branch predictor checker"
./branch_predictor_checker.sh "$outputs/branch_predictor" "$testcases/branch_predictor" "$outputs/branch_predictor_checker"
