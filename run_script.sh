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
echo -n > "$outputs/missing_invalid_zip"
for student in "$submission_dir"/*; do
    student_name=$(basename "$(ls "$student"/*_*_A2.zip 2> /dev/null)")
    if [ ${#student_name} != 30 ]; then
        echo "$student" >> "$outputs/missing_invalid_zip"
        continue
    fi
    unzip -o "$student/$student_name" -d "$student" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$student" >> "$outputs/missing_invalid_zip"
        continue
    fi
    student_dir=${student_name::-4}
    if [ ! -d "$student/$student_dir" ]; then
        echo "$student" >> "$outputs/missing_invalid_zip"
    fi
done

echo "Running pipeline code"
if [ ! -d "$outputs/pipeline" ]; then
    mkdir "$outputs/pipeline"
fi
echo -n > "$outputs/pipeline_compile_error"

for student in "$submission_dir"/*; do
    student_dir=$(basename "$(ls "$student"/*_*_A2.zip 2> /dev/null)")
    if [ ${#student_dir} != 30 ]; then
        continue
    fi
    student_dir=${student_dir::-4}
    if [ ! -d "$student/$student_dir" ]; then
        continue
    fi

    student_name=${student_dir::-3}
    if [ ! -d "$outputs/pipeline/$student_name" ]; then
        mkdir "$outputs/pipeline/$student_name"
    fi
    log_file="$wd/$outputs/pipeline/$student_name/log"
    echo -n > "$log_file"

    (cd "$student/$student_dir" > /dev/null 2>&1 && make -s compile >> "$log_file" 2>&1)
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
            cp "$testcase" "$student/$student_dir/input.asm"
            
            pushd "$student/$student_dir" > /dev/null 2>&1
            echo "5_nobypass" >> "$log_file"
            timeout 60 make -s run_5stage > "$wd/$outputs/pipeline/$student_name/$testcase_name/5_nobypass" 2>> "$log_file"
            echo "5_bypass" >> "$log_file"
            timeout 60 make -s run_5stage_bypass > "$wd/$outputs/pipeline/$student_name/$testcase_name/5_bypass" 2>> "$log_file"
            echo "79_nobypass" >> "$log_file"
            timeout 60 make -s run_79stage > "$wd/$outputs/pipeline/$student_name/$testcase_name/79_nobypass" 2>> "$log_file"
            echo "79_bypass" >> "$log_file"
            timeout 60 make -s run_79stage_bypass > "$wd/$outputs/pipeline/$student_name/$testcase_name/79_bypass" 2>> "$log_file"
            popd > /dev/null 2>&1
        fi
    done
done

echo "Running pipeline checker"
make -s -C "$unpipelined_wd" > /dev/null 2>&1
for testcase in "$testcases"/pipeline/*; do
    testcase_name=$(basename "$testcase")
    echo $testcase
    pushd "$unpipelined_wd" > /dev/null 2>&1
    ./sample  "$wd/$testcase" > "$wd/$pipeline_gold/$testcase_name/79"
    popd > /dev/null 2>&1
done

python3 pipeline_checker.py "$pipeline_gold" "$outputs"

echo "Running branch predictor code"
cp BranchPredictor.cpp "$workspace"/.
cp Makefile "$workspace"/.
if [ ! -d "$outputs/branch_predictor" ]; then
    mkdir "$outputs/branch_predictor"
fi
echo -n > "$outputs/branch_predictor_compile_error"

for student in "$submission_dir"/*; do
    student_dir=$(basename "$(ls "$student"/*_*_A2.zip 2> /dev/null)")
    if [ ${#student_dir} != 30 ]; then
        continue
    fi
    student_dir=${student_dir::-4}
    if [ ! -d "$student/$student_dir" ]; then
        continue
    fi

    student_name=${student_dir::-3}
    if [ ! -d "$outputs/branch_predictor/$student_name" ]; then
        mkdir "$outputs/branch_predictor/$student_name"
    fi

    if [ ! -f "$student/$student_dir/BranchPredictor.hpp" ]; then
        echo "$student_name" >> "$outputs/branch_predictor_compile_error"
        continue
    fi

    log_file="$wd/$outputs/branch_predictor/$student_name/log"
    echo -n > "$log_file"

    cp "$student/$student_dir/BranchPredictor.hpp" "$workspace/BranchPredictor.hpp"
    make -s -C "$workspace" BranchPredictor >> "$log_file" 2>&1
    if [ $? -ne 0 ]; then
        echo "$student_name" >> "$outputs/branch_predictor_compile_error"
        continue
    fi


    for testcase in "$testcases"/branch_predictor/*; do
        testcase_name=$(basename "$testcase")
        if [ ! -d "$outputs/branch_predictor/$student_name/$testcase_name" ]; then
            mkdir "$outputs/branch_predictor/$student_name/$testcase_name"
        fi

        echo "Running $testcase_name" >> "$log_file"
        for caseNum in {1..3}; do
            echo "Case $caseNum" >> "$log_file"
            for value in {0..3}; do
                echo "Value $value" >> "$log_file"
                timeout 60 ./"$workspace/BranchPredictor" "$testcase" $caseNum $value > "$outputs/branch_predictor/$student_name/$testcase_name/${caseNum}_$value" 2>> "$log_file" |:
            done
        done
    done
done

echo "Running branch predictor checker"
make -s BranchPredictorChecker
./BranchPredictorChecker "$outputs" "$testcases/branch_predictor"
