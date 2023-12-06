#!/usr/bin/env python3

import re


def parse_filename(filename):
    regex = r"(?P<orig_filename>.*)!(?P<type>[^!]{4})!(?P<creator>[^!]{4})(?P<residual_ext>.*)"
    match = re.search(regex, filename)
    print(match.groupdict())
    return


parse_filename("A lire absolument !!TEXT!ttxt.rsrc")
