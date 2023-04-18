# Set bash as the interpreter
#!/bin/bash

# get the input for the submission directory
submission_dir=$1
# make -C $submission_dir compile

test_case_name=$2
output_file='public_test4_a.out'
cp $2 $submission_dir/input.asm
# output the result of the test into a file without printing the command
make -s -C $submission_dir run_5stage > $submission_dir/$output_file
diff -b $submission_dir/$output_file 'Outputs'/$output_file





