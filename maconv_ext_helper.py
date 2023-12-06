#!/usr/bin/env python3

import re


def parse_filename(filename):
    regex = r"(?P<orig_filename>.*)!(?P<type>[^!]{4})!(?P<creator>[^!]{4})(?P<residual_ext>.*)"
    match = re.search(regex, filename)
    print(match.groupdict())
    return


parse_filename("A lire absolument !!TEXT!ttxt.rsrc")

# Algorithm

# Part 1 - get through file tree

# Part 2 - get, for each file, the type and creator

# Part 3 - First, check if file matches siegfried signature and get "normal" extension
# Part 3b - Add type,creator and extension from siegfried to database

# Part 4 - If no match, search TCDB for type and creator, and existing matching extension

# Part 5 - Rename file with proper extension if possible
# Part 5b - If no extension, keep type as extension

