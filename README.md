# COL216 Assignment 2 Autograder

## Running Submissions
1. The submissions are in the directory `<submissions>`. This directory contains a sub-directory for each student.
2. The workspace directory is `<workspace>`. This directory will run the branch predictor.
3. The testcases are in the directory `<testcases>`. This directory contains two sub-directories - `pipeline` and `branch_predictor`. Each of these sub-directories contains a sub-directory for each testcase.
4. The outputs of the students will be stored in the directory `<outputs>`. On running the script, the following files and directories will be created,
```
├── <outputs>
│   ├── branch_predictor
│   │   ├── <directory for each student>
│   │   │   ├── <directory for each testcase>
│   ├── branch_predictor_csvs
│   │   ├── <csv file for each testcase>
│   ├── pipeline
│   │   ├── <directory for each student>
│   │   │   ├── <directory for each testcase>
│   ├── pipeline_csvs
│   │   ├── <csv file for each testcase>
|   ├── branch_predictor_compile_errors
|   ├── missing_invalid_zip
|   ├── pipeline_compile_errors
```
5. The gold solutions for pipeline are in the `<pipeline_gold>` directory. This directory contains a sub-directory for each testcase. Each sub-directory contains three files `5_nobypass`, `5_bypass` and `79`, containing the outputs for each of them.
6. The directory containing the unpipelined code is `<unpipelined_code>`. This will be run to generate the `79` gold outputs for `<pipeline_gold>`.
7. To run the submissions, run the following command:
```
$ ./run_script.sh <submissions> <workspace> <testcases> <outputs> <pipeline_gold> <unpipelined_code>
```

## Pipeline Simulator
1. After all submissions are run, the pipeline outputs will be in the directory `<pipeline_outputs>`. This directory will contain a sub-directory for each testcase. Each testcase directory contains a directory for each submission. Each submission output directory contains 4 files for each of the parts.
2. The gold outputs are in the directory `<gold>`. This contains a sub-directory for each test case. Each sub-directory contains three files `5_nobypass`, `5_bypass` and `79`, containing the outputs for each of them.
3. To run the pipeline simulator, run the following command:
```
$ python3 pipeline_checker.py <gold> <pipeline_outputs>
```

## Branch Predictor Simulator
1. After all submissions are run, the branch predictor outputs will be in the directory `<branch_outputs>`. This directory will contain a sub-directory for each testcase. Each testcase directory contains a directory for each submission. Each submission output directory contains 12 files - 3 different predictors each initialised with 4 different values.
2. To run the branch predictor simulator, run the following command:
```
$ make BranchPredictorChecker
$ ./BranchPredictorChecker <branch_outputs> <traces_directory>
```