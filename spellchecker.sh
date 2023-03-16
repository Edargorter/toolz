#!/bin/bash

readarray -t file_arr < exclusions.txt

echo $file_arr
regex_str=""

for file in "${file_arr[@]}"; do
	# file=$(echo $file | sed 's/\./\\\./g' | sed 's/\*/\.\*/g')
	regex_str=$regex_str"|($file)"
done

regex_str="${regex_str:1}"
echo $regex_str

# exit 1

for file in $(find . -type f -print); do
	reg_file=$(echo "$file" | sed 's|\/|\\/|g')
	# echo $reg_file
	if [[ "$reg_file" =~ $regex_str ]]; then
		# echo "$file"
		continue
	fi
	cat $file | aspell list | sed "s|.*|$file &|" 
done
