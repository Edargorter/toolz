#!/usr/bin/env python3

from sys import argv 

encoding = "ISO-8859-1"
outencode = "utf-8"

try:
    filename = argv[1]
    service = argv[2]
    datefile = argv[3]
    if len(argv) > 4:
        encoding = argv[4]
except Exception as e:
    print("Usage: python3 {} filename servicename datesfile [ encoding ]".format(argv[0]))
    exit(1)

try:
    print("Reading data...", end="\r")
    f = open(filename, 'r', encoding=encoding)
    size = sum(1 for line in f)
    f.close()
    f = open(filename, 'r', encoding=encoding)
    print("Done")
    dates = [x.strip() for x in open(datefile, 'r').readlines()]
    print(dates)
except Exception as e:
    print(e)
    exit(1)

out = {}
for date in dates:
    out[date] = open("{}_{}.csv".format(service, date.replace(' ', '_').replace(',', '')), 'w')

count = 0
print(out)

print("Separating...")

for line in f:
    if count == 0: #Column headings 
        for date in dates:
            out[date].write(str(line.encode(outencode)))
        count += 1
        continue
    for date in dates:
        if date in line:
            out[date].write(str(line.encode(outencode)))
            break
    count += 1
    print("Progress: {}%".format(round(100 * count / size), 2), end="\r")

print("Done")

for d in out:
    out[d].close() 

f.close()
