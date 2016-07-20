#---------------------------------------------------------------------------#
# Create XBEL bookmarks file from Firefox's places.sqlite 
# The output can be rendered nicely in a web-browser using XSLT
# ? Which XSLT 
# ? Credit
#---------------------------------------------------------------------------#

import os
import sqlite3
import configparser
from xml.sax.saxutils import escape
import pdb


##
# http://kb.mozillazine.org/Profile_folder_-_Firefox
def find_mozilla_places_db():
    # Linux only
    # All bets are off if the profile folder is changed.
    profileFile = r'/home/{0}/.mozilla/firefox/profiles.ini'.format(
        os.getenv('USER'))
    if not os.path.exists(profileFile):
        print("Mozilla Firefox profile not found. Exiting.")
        sys.exit(0)
    mozProfile = configparser.ConfigParser()
    mozProfile._interpolation = configparser.ExtendedInterpolation()
    mozProfile.read(profileFile)
    mozProfile.sections()
    mozProfilePath = mozProfile.get('Profile0', 'Path')
    profileFolder = r'/home/{0}/.mozilla/firefox'.format(os.getenv('USER'))
    return os.path.join(profileFolder, mozProfilePath, r'places.sqlite')


##
# Found a bookmark which needs processing
def process_bookmark(foreign_key, db):
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
def process_folder(an_id, db):
    #pdb.set_trace()
    conn=sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Prep. folder
    sql = r'SELECT * FROM moz_bookmarks WHERE id = {0}'.format(an_id);
    for row in c.execute(sql):
         print("<folder FOLDERID=\"{0}\">".format(escape(row['title'])))
         print("<title>{0}</title>".format(escape(row['title'])))
    # Process remaining
    sql = r'SELECT * FROM moz_bookmarks WHERE PARENT = {0}'.format(an_id)
    # todo FOLDER info. should be set here.
    for row in c.execute(sql):
        if row['fk'] is None:
            # Call self
            process_folder(row['id'], db)
        else:
            # Process the bookmark
            print("<bookmark href=\"{0}\" bmid=\"{1}\">".format(
                process_bookmark(row['fk'], db)['href'], row['guid']))
            print("<title>{0}</title>".format(escape(row['title'])))
            print("</bookmark>")
    conn.close()
    print("</folder>")


##
#
def main(argv=None):
    # Find Mozilla profile dir
    db = find_mozilla_places_db() 
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
        process_folder(folder, db)
    print(r'</xbel>')


if __name__ == '__main__':
    main()
