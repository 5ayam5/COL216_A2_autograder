rm -rf old new
if [ $# -ne 1 ]; then
    echo "give me a name!"
    exit 1
fi
name=$1
clear

cp ../submissions/"$name"* old -r
if [ $? != 0 ]; then
    echo "didn't submit earlier"
    exit 1
fi

cp ../resubmissions/"$name"* new -r
if [ $? != 0 ]; then
    rm -rf old
    echo "didn't re-submit"
    exit 1
fi

declare -a arr=("old" "new")
for dir in "${arr[@]}"; do
    zip_name=$(basename "$(ls "$dir"/*.zip 2> /dev/null)")
    mkdir "$dir/folder" > /dev/null 2>&1
    unzip -o  "$dir/$zip_name" -d "$dir/folder" > /dev/null 2>&1
    rm -rf "$dir/folder/__MACOSX"
done

zip_name=$(basename "$(ls "${arr[1]}"/*.zip 2> /dev/null)")
if [ ! -d "${arr[1]}/folder/${zip_name::-4}" ]; then
    rm -rf old new
    echo "didn't unzip correctly"
    exit 2
fi
arr[1]="${arr[1]}/folder/${zip_name::-4}"

ls -d "${arr[0]}"/folder/*/ > /dev/null 2>&1
if [ $? -eq 0 ] && [ $(ls -d "${arr[0]}"/folder/*/ | wc -l) -eq 1 ]; then
    arr[0]=$(ls -d "${arr[0]}"/folder/*/)
    if [ $(basename ${arr[1]}) = $(basename ${arr[0]}) ]; then
        echo "zip format was fine"
    else
        echo "zip format was incorrect"
    fi
else
    arr[0]="${arr[0]}/folder"
    echo "zip format was incorrect"
fi

colordiff "${arr[0]}" "${arr[1]}" -r
