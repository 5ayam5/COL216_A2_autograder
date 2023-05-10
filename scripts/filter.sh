if [ $# -ne 3 ]; then
    echo "Usage: $0 <resubmissions.csv> <resubmissions dir> <output dir>"
    exit 1
fi

resubmissions_dir=$2
output_dir=$3

python3 filter_resubmissions.py $1 |
while IFS="" read -r p || [ -n "$p" ]; do
    cp "$resubmissions_dir/$p"* "$output_dir/." -r
done
