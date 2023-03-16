#!/bin/bash

listfile=$1
searchfile=$2
if [ $# -eq 0 ]
then
	echo -e "Run with:\n lgrep list_file search_file"
	exit 1
elif [ $# -eq 1 ]
then
	echo -e "Please provide path to search file."
	exit 2
fi

grep -ir "$(awk -vORS='|' '{ print $1 }' $2 | sed 's/,$/\n')"
