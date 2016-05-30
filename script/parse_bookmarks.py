# ------------------------------------------------------------------------- #
# Convert Mozilla bookmarks export (json) to xbel
# ------------------------------------------------------------------------- #

import os
import sys
import json
import getopt
from xml.sax.saxutils import escape
import pdb

##
#
def createBMTag(jsonBMDict):
    print('found place')
    # Based on Mozilla spec
    mozSpecD = {
            'uri': 'bookmark', 
            'title': 'title',
            }
    # For metadata xbel tag
    forMetadata = [
            'lastModified',
            'dateAdded',
            ]
    # Produce string to insert into output
    bmStr = '' 
    for k, v in mozSpecD.items():
        if v == 'bookmark':
            # Set up bookmark tag - leave open until other tags have been 
            # parsed.
            #bmStr = "<{0} href=\"{1}\"".format(v, jsonBMDict[k])
            bmStr = "{0}{1}".format("<{0} href=\"{1}\">".format(v,
                escape(jsonBMDict[k])), bmStr)
        elif v in forMetadata:
            pass
        else:
            bmStr = "{0}{1}".format(
                    bmStr,
                    r"<{0}>{1}</{0}>".format(v, escape(jsonBMDict[k])))
    # Close up the bookmark tag
    bmStr = "{0}</bookmark>".format(bmStr)
    return bmStr

##
#
def hasChildren(child, out_f):
    print('checking hasChildren...')
    if type(child) == list:
        # Either a list of places or mix of places + folders
        print('found list')
        for cld in child:
            if cld['type'] == r'text/x-moz-place':
                bmStr = createBMTag(cld)
                out_f.write(bmStr)
            elif (cld['type'] == r'text/x-moz-place-container'):
                out_f.write(
                        "<folder FOLDERID=\"{0}\"><title>{0}</title>".format(
                            cld['title']))
                if 'children' in cld.keys():
                    hasChildren(cld['children'], out_f)
                out_f.write("</folder>")
    elif type(child) == dict and child['children']:
        out_f.write(
                "<folder FOLDERID=\"{0}\"><title>{0}</title>".format(
                    child['title']))
        hasChildren(child['children'], out_f)
        out_f.write("</folder>")
    else:
        # erm.
        print('no child found')
        pdb.set_trace()

##
#
def parseJSON(in_f, out_f):
    #data = json.loads(open(in_f).read())
    # alt. read.
    with open(in_f, encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
    # dict_keys(['guid', 'type', 'id', 'dateAdded', 'root', 'index', 'title',
    # 'lastModified', 'children'])
    # 'children' represent the folder structure. The keys are present for 
    # each bookmark and folder as selected.
    # XBEL permits grouping by folder.

    # Process one child at a time.
    # type,text/x-moz-place-container
    # type,text/x-moz-place
    # root folder has dict key 'root'

    # Set up out file
    out_f_writer = open(out_f, 'w')

    out_f_writer.write("""<?xml version="1.0"?>
    <!DOCTYPE xbel PUBLIC 
    "+//IDN python.org//DTD XML Bookmark Exchange Language 1.0//EN//XML" 
    "http://www.python.org/topics/xml/dtds/xbel-1.0.dtd">
<xbel version=\"1.0\">
""")

    # Selecting 'Unsorted bookmarks' only.
    my_list = [data['children'][2]]
    for child in my_list:
        if child['children']:
            print('has children')
            hasChildren(child, out_f_writer)
            # send to self.
        else:
            print('no children')
            pdb.set_trace()

    out_f_writer.write("</xbel>")
    out_f_writer.close()

##
#
def usage():
    print('python moz_bm_json_to_xbel.py')
    print('  -f <file> (required)')
    print('  -h <help> (optional)')

##
#
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:", ["help", "file="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    inputFile = None
    outputFile = None
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-f', '--file'):  
            inputFile = a
        else:
            assert False, "unhandled option"
    if inputFile is None:
        usage()
        sys.exit()
    # Check intpuFile exists
    if not os.path.exists(inputFile):
        usage()
        sys.exit(r'File "{0}" not found.'.format(inputFile)) 
    ofPath, ofExt = os.path.splitext(inputFile)
    outputFile = "{0}.xml".format(ofPath)
    # Parse and process the JSON export
    parseJSON(inputFile, outputFile)
    # Parse and process the HTML export
    # todo.
    print('End.')


if __name__ == '__main__':
    main()
