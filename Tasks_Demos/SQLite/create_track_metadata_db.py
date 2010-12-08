"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code creates an SQLite dataset that contains one row
per track and has all the regular metadata.

This is part of the Million Song Dataset project from
LabROSA (Columbia University) and The Echo Nest.


Copyright 2010, Thierry Bertin-Mahieux

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import glob
try:
    import sqlite3
except ImportError:
    print 'you need sqlite3 installed to use this program'
    sys.exit(0)


def encode_string(s):
    """
    Simple utility function to make sure a string is proper
    to be used in a SQLite query
    (different than posgtresql, no N to specify unicode)
    EXAMPLE:
      That's my boy! -> 'That''s my boy!'
    """
    return "'"+s.replace("'","''")+"'"


def create_db(filename):
    """
    Creates the file and an empty table.
    """
    # creates file
    conn = sqlite3.connect(filename)
    # add stuff
    c = conn.cursor()
    c.execute('''CREATE TABLE SONGS (track_id text, artist_id text, duration real)''')
    # commit and close
    conn.commit()
    c.close()
    conn.close()



def fill_from_h5(conn,h5path):
    """
    Add a row witht he information from this .h5 file
    Doesn't commit, doesn't close conn at the end!
    """
    h5 = hdf5_utils.open_h5_file_append(h5path)
    c = conn.cursor()
    # build query
    q = 'INSERT INTO SONGS VALUES ('
    track_id = get_track_id(h5)
    q += encode_string(track_id)
    artist_id = get_artist_id(h5)
    q += ', '+encode_string(artist_id)
    duration = str(get_duration(h5))
    q += ", "+duration
    # query done, close h5, commit
    h5.close()
    q += ')'
    c.execute(q)
    #conn.commit() # we don't take care of the commit!
    c.close()


def die_with_usage():
    """ HELP MENU """
    print 'Command to create the track_metadata SQLite database'
    print 'to launch (it might take a while!):'
    print '   python create_track_metadata_db.py <MillionSong dir> <track_metadata.db>'
    print 'PARAMS'
    print '  MillionSong dir   - directory containing .h5 song files in sub dirs'
    print '  track_metadata.db - filename for the database'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # import HDF5 stuff
    pythonsrc = os.path.join(sys.argv[0],'../../../PythonSrc')
    pythonsrc = os.path.abspath( pythonsrc )
    sys.path.append( pythonsrc )
    import hdf5_utils
    from hdf5_getters import *

    # read params
    maindir = os.path.abspath(sys.argv[1])
    dbfile = os.path.abspath(sys.argv[2])

    # check if file exists!
    if os.path.exists(dbfile):
        print dbfile,'already exists! delete or provide a new name'
        sys.exit(0)

    # create dataset
    create_db(dbfile)

    # open connection
    conn = sqlite3.connect(dbfile)
    
    # iterate HDF5 files
    cnt_files = 0
    for root, dirs, files in os.walk(maindir):
        files = glob.glob(os.path.join(root,'*.h5'))
        for f in files :
            fill_from_h5(conn,f)
            cnt_files += 1
            if cnt_files % 50 == 0:
                conn.commit() # we commit only every 50 files!

    # commit and close connection
    conn.commit()
    conn.close()

    # DONE
    print 'done! added the content of',cnt_files,'files to database:',dbfile
    