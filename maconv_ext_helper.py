#!/usr/bin/env python3

import re
import sys, os

def parse_filename(filename):
    regex = r"(?P<orig_filename>.*)!(?P<type>[^!]{4})!(?P<creator>[^!]{4})(?P<residual_ext>.*)"
    match = re.search(regex, filename)
    print(match.groupdict())
    return

def list_files(start_path):
    for root, dirs, files in os.walk(start_path):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                encoded_path = file_path.encode('utf-8', 'surrogatepass').decode('utf-8')
                print(encoded_path)
            except Exception as e:
                print(e)

                

parse_filename("A lire absolument !!TEXT!ttxt.rsrc")

# Algorithm

# Part 1 - get through file tree
# Possible issue: maconv extracts files with Mac Roman encoding, without converting it, which is not UTF-8
# Should use convmv --nosmart -f MacRoman -t utf8 -r --preserve-mtimes /folder
path = sys.argv[1]
list_files(path)



# Part 2 - get, for each file, the type and creator

# Part 3 - First, check if file matches siegfried signature and get "normal" extension
# Part 3b - Add type,creator and extension from siegfried to database

# Part 4 - If no match, search TCDB for type and creator, and existing matching extension

# Part 5 - Rename file with proper extension if possible
# Part 5b - If no extension, keep type as extension

