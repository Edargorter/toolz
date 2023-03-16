#!/bin/bash 

if [ -z "$1" ]
then
	echo "No filename provided"
	exit 1
else
	filename="$1"
fi

echo "File: $filename"

if [ -z "$2" ]
then
	echo "Please provide word list."
	exit 1
else
	wordlist="$2"
fi

echo "Word list: $wordlist"

if [ -z "$3" ]
then
	outfile="results.txt"
else
	outfile="$3"
fi

wcl=$(wc -l "$filename" | cut -d " " -f 1)
words=$(cat $wordlist)
wlwc=$(wc -l $wordlist | cut -d " " -f 1)
echo "Lines: $wcl" 
index=0
prog=0
prev_size=0
lines=0

for st in $words
do
	echo -n "Word: $st"
	grep -ir $st $filename >> $outfile 
	curr=$(wc -l $outfile | cut -d " " -f 1)
	lines=$(( $curr - $prev_size ))
	echo -en " \t\t --- Lines: $lines --- Progress: $prog%\n"
	prev_size=$curr
	index=$(($index+1))
	prog=$(expr $((100 * $index)) / $wlwc)
done

echo "Done. See results in $outfile."
