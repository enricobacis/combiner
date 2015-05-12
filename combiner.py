#!/usr/bin/env python

from os.path import basename, dirname, join, isfile
import argparse
import re

include = re.compile(r'^\s*#include\s+"(.*?)"\s*$', re.MULTILINE)
headers = set()
sources = set()

def process_header(header, cfile, hfile):
    if header in headers:
        hfile.write('\n/* %s already was included */\n\n' % basename(header))
    else:
        print 'processing header file %s' % header
        headers.add(header)
        hfile.write('\n/* start of file %s */\n\n' % basename(header))
        with open(header) as f:
            for line in f.readlines():
                if include.match(line):
                    included = include.match(line).group(1)
                    path = join(dirname(header), included)
                    process_header(path, cfile, hfile)
                else:
                    hfile.write(line)
        hfile.write('\n/* end of file %s */\n\n' % basename(header))
        process_source(header.replace('.h', '.c'), cfile, hfile)


def process_source(source, cfile, hfile):
    if isfile(source) and source not in sources:
        print 'processing source file %s' % source
        sources.add(source)
        with open(source) as f:
            cfile.write('\n/* start of file %s */\n\n' % basename(source))
            for line in f:
                if include.match(line):
                    included = include.match(line).group(1)
                    path = join(dirname(source), included)
                    process_header(path, cfile, hfile)
                else:
                    cfile.write(line)
            cfile.write('\n/* end of file %s */\n\n' % basename(source))

if __name__ == '__main__':
    parser = argparse.ArgumentParser( description='Generate combined .c/.h files')
    parser.add_argument('input', nargs='+', metavar='INPUT',
            type=str, help='Input .c/.h files')
    parser.add_argument('-o', '--output', default='output',
            type=str, help='Output base name')
    args = parser.parse_args()

    with open(args.output + '.c', 'w') as cfile:
        with open(args.output + '.h', 'w') as hfile:
            cfile.write('#include "%s"\n\n' % hfile.name)
            for input in args.input:
                if input.endswith('.c'):
                    process_source(input, cfile, hfile)
                elif input.endswith('.h'):
                    process_header(input, cfile, hfile)
                else:
                    print 'ERROR: unkown extension for %s' % input

