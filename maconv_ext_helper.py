#!/usr/bin/env python3

import re
import sys, os
import subprocess
import pathlib
import json
import pandas
from rich import print

def parse_filename(filename):
    regex = r"(?P<orig_filename>.*)!(?P<type>[^!]{3,})!(?P<creator>[^!]{3,4})(?P<residual_ext>\.rsrc)?"
    match = re.search(regex, filename)
    fileName = match.groupdict()['orig_filename']
    fileType = match.groupdict()['type']
    fileCreator = match.groupdict()['creator']
    fileResidualExt = match.groupdict()['residual_ext']
    if not fileResidualExt:
        fileResidualExt = ""
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
tcdb_path = 'updated_TCDB.csv'

tcdbData = pandas.read_csv(tcdb_path, sep=";")

# 3 potential sources of extensions
# 1 - Existing extension, but might be wrong
# 2 - Siegfried, most certainly the most precise and trustworthly
# 3 - TCDB, based on MacOS Type and Creator, might be wrong


# Part 1 - get through file tree
# Possible issue: maconv extracts files with Mac Roman encoding, without converting it, which is not UTF-8
# You could use `convmv --nosmart -f MacRoman -t utf8 -r --preserve-mtimes /folder` to solve the problem
path = sys.argv[1]
for filepath in list_files(path):
    existingExt=''
    sfPUID = 'UNKNOWN'
    finalExt = ''
    tcdbExtension = ''
    sfExtensions = ''

    filename = os.path.basename(filepath)
    
    print(filepath)
        
    # TODO - Check if already existing extension
    # We might want to keep the existing? Or check consistency with the other information sources (SF, TCDB).

    # Part 2 - get, for each file, the type and creator
    try:
        fileName, fileType, fileCreator, fileResidualExt = parse_filename(filename)
        print(filename)
        print("# INFO - Name: ^[bold]"+str(fileName)+"[/bold]$ (length "+str(len(fileName))+")")
        print("# INFO - Type ^[bold]"+str(fileType)+"[/bold]$")
        print("# INFO - Creator ^[bold]"+str(fileCreator)+"[/bold]$") 
        print("# INFO - ResidualExt ^[bold]"+str(fileResidualExt)+"[/bold]$")
    except:
        continue

    # Check if already existing extension
    # We might want to keep the existing? Or check consistency with the other information sources (SF, TCDB).
    existingExt = pathlib.Path(fileName).suffix
    print("# INFO - Existing ext: ", existingExt)


    # Call siegfried
    sfJson = siegfried(filepath)
    sfData = json.loads(sfJson)
    #print(sfData)
    sfPUID = sfData["files"][0]["matches"][0]["id"]
    

    # Part 3 - First, check if file matches siegfried signature and get "normal" extension
    if sfPUID != "UNKNOWN":
        # Part 3 - Matching in siegfried
        print("# INFO - Siegfried Pronom Unique ID (PUID): "+sfPUID)
        
        # Get extension from pronom JSON?
        with open("pronom_v111.json", "r") as f:
            pronom_data = json.load(f)

        sfExtensions = pronom_data[sfPUID]["file_extensions"]
        print("# INFO - Extensions: ", sfExtensions)
        # Part 3b - Add type,creator and extension from siegfried to database

    else:
        # Part 4 - If no match, search TCDB for type and creator, and existing matching extension
        print("# INFO - Unknown to Siegfried")

    try:
        df = tcdbData[tcdbData['Type'].str.contains(fileType) & tcdbData['Creator'].str.contains(fileCreator)]
        if not df.empty:
            print("# DEBUG - TCDB entries")
            print(df.to_string(header=False))
            tcdbExtension = str(df.iloc[0]['Extension']).strip()
            print("# INFO - TCDB extension: ^"+tcdbExtension+"$")
        else:
            print("# INFO - No match in TCDB")

    except:
        print("Error")

    # Part 5 - Confront all extension information and choose
    # If no extension at all, put MacOS type lowercased as extension

    winner = ""
    if sfPUID != "UNKNOWN" and sfExtensions:
        winner="SF"
        finalExt = "."+str(sfExtensions[0])
  
    elif len(str(tcdbExtension))>0 and "nan" not in str(tcdbExtension):
        winner="TCDB"
        finalExt = "."+str(tcdbExtension)
    
    elif existingExt:
        winner="Existing"
        finalExt = str(existingExt)

    elif not winner:
        winner="Type"
        finalExt = "."+str(fileType.lower())

    if fileType == "APPL" and winner=='TCDB':
        winner="APPL"
        finalExt = ""

    print("Final extension ("+winner+"): [red]"+finalExt+"[/red]")

    # Part 6 - Rename file with proper extension if possible
    # Do not forget residual ext (usually .rsrc for resource files)
    parentDir = os.path.dirname(filepath)
    fileNoExt = os.path.splitext(fileName)[0]
    print(fileResidualExt)
    print("mv '"+filepath+"' '"+parentDir+"/"+fileName+finalExt+fileResidualExt+"'")
    os.rename(filepath, parentDir+"/"+fileNoExt+finalExt+fileResidualExt)

    print("------")
