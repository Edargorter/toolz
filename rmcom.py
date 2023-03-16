#!/usr/bin/env python3

from sys import argv
import argparse

'''
Name: rmcom ReMove COMments 
Author: Zachary Bowditch (Edargorter) 
Date: 2020
Description: Remove language-specific single/multi-line comments 
Status: Incomplete

'''

error_count = 0

def _exit(msg, n):
    print(msg)
    exit(n)

#Language specific single/multiline comments 
langs = {"C/C++": [["//"], [["/**", "**/"]]],
        "Python": [["#"], [["\'\'\'", "\'\'\'"]]],
        "JavaScript": [["//"], [["/*", "*/"]]],
        "Bash": [["#"], None],
        "HTML": [None, [["<!--", "-->"]]],
        "PHP": [["#", "//"], [["/*", "*/"]]]
        }

file_extensions = {"cpp": "C/C++",
                    "c": "C/C++",
                    "py": "Python",
                    "js": "JavaScript",
                    "html": "HTML",
                    "php": "PHP",
                    "sh": "BASH",
                    "bash": "BASH"
                  }

parser = argparse.ArgumentParser(description="ReMove COMments - The Ultimate Comment Remover\n...but can also remove any line(s) preceeded by a singleline comment char or in between multiline comments.")
parser.add_argument("-b", "--backup", metavar="backup", help="Turn backup on or off.")
parser.add_argument("-p", "--pattern", metavar="pattern", type=str, help="The comment character(s) (single / two for multiline). E.g. /** **/", nargs='+')
parser.add_argument("filename", metavar="filename", type=str, help="the source file (with file extension). E.g. prog.cpp")

args = parser.parse_args()
filename = args.filename

error_count += 1

fe = filename.split(".")[-1]  #File extension

if not fe:
    _exit("No file provided.", error_count)
lang = file_extensions[fe]

error_count += 1

#Make backup of file
if args.backup:
    copy2(filename, "{}.backup".format(filename))

try:
    f = open(filename, "r+")
except Exception as e:
    _exit(e, error_count)

lines = f.readlines()
f.close()

#Test patterns
'''
oneline = "//"
start = "<!--"
end = "-->"
'''
patterns = []

#If comment patterns were specified by user
if args.pattern:
    if len(args.pattern) == 1:
        patterns = [[args.pattern[0], '\n']]
    else:
        patterns = [args.pattern[:2]]
else:
    sl = langs[lang][0]
    ml = langs[lang][1]
    if sl:
        patterns += [[c, '\n'] for c in sl]
    if ml:
        patterns += ml
    patterns = sorted(patterns, key = lambda x : len(x[0]))

n = len(patterns)

out_file = "out_{}".format(filename)
f = open("{}".format(out_file), 'w')

index = 0
match = False
subs = [True for i in range(n)]

for line in lines:
    for c in line:
        can_write = True
        for p in range(n):
            if index == len(patterns[p][match]):
                match = not match
                index = 0
                subs = [True for i in range(n)]
                break
        for p in range(n):
            if subs[p]:
                if c == patterns[p][match][index]:
                    can_write = False
                    index += 1
                else:
                    subs[p] = False
        if can_write and not match:
            #Write to new file
            if index:
                first = 0
                for p in range(n):
                    if subs[p]:
                        first = p
                        break
                f.write(patterns[first][match][:index]) #Flush detached prefix 
            f.write(c)
            index = 0

f.close()
print("Done. View {}".format(out_file))
