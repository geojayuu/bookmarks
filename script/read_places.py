#---------------------------------------------------------------------------#
# Create XBEL bookmarks file from Firefox's places.sqlite 
# The output can be rendered nicely in a web-browser using XSLT
# ? Which XSLT 
# ? Credit
#---------------------------------------------------------------------------#

import os
import sqlite3
from xml.sax.saxutils import escape
import pdb

db = r'/home/{0}/.mozilla/firefox/wpatskez.default/places.sqlite'.format(
	os.getenv('USER'))

##
# Found a bookmark which needs processing
def process_bookmark(foreign_key):
    conn=sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    sql = r'SELECT id,url FROM moz_places WHERE ID = {0}'.format(foreign_key)
    rs = {r'href':r''}
    for row in c.execute(sql):
        rs[r'href'] = escape(row['url'])
    return rs

##
# Found a folder which needs processing
def process_folder(an_id):
    conn=sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Prep. folder
    sql = r'SELECT * FROM moz_bookmarks WHERE id = {0}'.format(an_id);
    for row in c.execute(sql):
         print("<folder FOLDERID=\"{0}\">".format(escape(row['title'])))
         print("<title>{0}</title>".format(row['title']))
    # Process remaining
    sql = r'SELECT * FROM moz_bookmarks WHERE PARENT = {0}'.format(an_id)
    # todo FOLDER info. should be set here.
    for row in c.execute(sql):
        if row['fk'] is None:
            # Call self.
            process_folder(row['id'])
        else:
            # Process the bookmark
            print("<bookmark href=\"{0}\" bmid=\"{1}\">".format(
                process_bookmark(row['fk'])['href'], row['guid']))
            print("<title>{0}</title>".format(escape(row['title'])))
            print("</bookmark>")
    conn.close()
    print("</folder>")

##
#
def main(argv=None):
    # Set up file
	print("""<?xml version="1.0"?>
	<!DOCTYPE xbel 
	PUBLIC "+//IDN python.org//DTD XML Bookmark Exchange Language 1.0//EN//XML" 
	"http://www.python.org/topics/xml/dtds/xbel-1.0.dtd">
<xbel version="1.0">""")
    # We want to process all folders in 'All Bookmarks'
    # - Bookmarks Menu/Mozilla Firefox      (id 27)
    # - Unsorted Bookmarks                  (id 5)
	folder_ids = ['27', '5']
	for folder in folder_ids:
		process_folder(folder)
	print(r'</xbel>')

if __name__ == '__main__':
    main()
