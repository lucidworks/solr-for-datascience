__author__ = 'grantingersoll'

import optparse
import random


#
# Small script to create samples from the original Citibike data
#
def sample(input_file, output_file, rows):
    print "Sampling " + str(rows) + " from " + input_file + " and writing to " + output_file
    j = 0
    output = open(output_file, 'w')
    f = open(input_file)
    lines = f.readlines() # there is probably a better way to do this w/o reading the whole file, but the files are only 150mb
    output.write(lines.pop(0))
    seen = set()
    length = len(lines)
    for i in range(0, length):
        val = random.randint(0, length)
        if val not in seen:
            output.write(lines[val])
            seen.add(val)
            j += 1
        if j >= rows:
            print "here"
            break

    print "Wrote " + str(j) + " lines to " + output_file
    output.close()

p = optparse.OptionParser()
p.add_option("-i", "--input", action="store", dest="input")
p.add_option("-o", "--output", action="store", dest="output")
p.add_option("-r", "--rows", action="store", dest="rows");
opts, args = p.parse_args()

sample(opts.input, opts.output, int(opts.rows))
