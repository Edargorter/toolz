#!/bin/bash

# Usage: spellcheck -n number
#
# where "number" is the line number of the typo you wish to correct

if [[ "$1" -eq "-n" ]]; then
	n=$2
	details=$(cat "spelling_errors_"* | head -n $n | tail -n 1)
	filename=$(echo $details | cut -d " " -f 1)
	typo=$(echo $details | cut -d " " -f 2)
	echo $filename 
	echo $typo
	echo $typo | xclip -sel clip 
	vim $filename 
	exit 1
fi

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

out_file="spelling_errors_$(echo $RANDOM | base64 | head -c 7).txt"
touch "$out_file"

for file in $(find . -type f -print); do
	# reg_file=$(echo "$file" | sed 's|\/|\\/|g')
	# echo $reg_file
	if [[ $regex_str != "" ]] && [[ "$file" =~ $regex_str ]]; then
		# echo "$file"
		continue
	fi
	errors=$(cat $file | aspell list | sed "s|.*|$file &|") # | sed 's/$/&\\n/g')

	echo -en "$errors"
	echo -en "$errors" >> $out_file 
done
