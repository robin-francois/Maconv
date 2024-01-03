#!/usr/bin/env python3

import re
import sys, os
import subprocess
import json
import pandas
from rich import print

def parse_filename(filename):
    regex = r"(?P<orig_filename>.*)!(?P<type>[^!]{4})!(?P<creator>[^!]{4})(?P<residual_ext>.*)"
    match = re.search(regex, filename)
    fileName = match.groupdict()['orig_filename']
    fileType = match.groupdict()['type']
    fileCreator = match.groupdict()['creator']
    fileResidualExt = match.groupdict()['residual_ext']
    return fileName, fileType, fileCreator, fileResidualExt

def list_files(start_path):
    file_list = list()
    for root, dirs, files in os.walk(start_path):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                encoded_path = file_path.encode('utf-8', 'surrogatepass').decode('utf-8')
                file_list.append(encoded_path)
            except Exception as e:
                print(e)
    return file_list

def siegfried(filepath):
    cmd = ["sf", "-json", filepath]
    try:
        sfJson = subprocess.check_output(cmd)
    except Error as e:
        print(e)
        print("Error with siegfried")
        sys.exit(1)
    return sfJson

# Algorithm

# Loading resource files

# Loading TCDB into pandas
tcdb_path = 'TCDB_2003.8_data_utf8.csv'

tcdbData = pandas.read_csv(tcdb_path, sep=";")

# Part 1 - get through file tree
# Possible issue: maconv extracts files with Mac Roman encoding, without converting it, which is not UTF-8
# You could use `convmv --nosmart -f MacRoman -t utf8 -r --preserve-mtimes /folder` to solve the problem
path = sys.argv[1]
for filepath in list_files(path):
    filename = os.path.basename(filepath)
    
    # Part 2 - get, for each file, the type and creator
    fileName, fileType, fileCreator, fileResidualExt = parse_filename(filename)
    print(fileName, fileType, fileCreator, fileResidualExt)
    print("# INFO - Name: ^[bold]"+str(fileName)+"[/bold]$ (length "+str(len(fileName))+")")
    print("# INFO - Type ^[bold]"+str(fileType)+"[/bold]$")
    print("# INFO - Creator ^[bold]"+str(fileCreator)+"[/bold]$") 

    # Call siegfried
    sfJson = siegfried(filepath)
    sfData = json.loads(sfJson)
    #print(sfData)
    sfId = sfData["files"][0]["matches"][0]["id"]
    

    # Part 3 - First, check if file matches siegfried signature and get "normal" extension
    if sfId != "UNKNOWN":
        # Part 3 - Matching in siegfried
        print("# INFO - Siegfried ID: "+sfId)
        
        # TODO - Get extension from pronom JSON?

        # Part 3b - Add type,creator and extension from siegfried to database

    else:
        # Part 4 - If no match, search TCDB for type and creator, and existing matching extension
        print("# INFO - Unknown to Siegfried")

    df = tcdbData[tcdbData['Type'].str.contains(fileType) & tcdbData['Creator'].str.contains(fileCreator)]
    if not df.empty:
        print(df)
    else:
        print("# INFO - No match in TCDB")

    # Part 5 - Rename file with proper extension if possible
    # Part 5b - If no extension, keep type as extension
    print("------")
