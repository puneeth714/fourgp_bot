#check if data database exists in fourgp/database/ and create it if not
import os
import sqlite3
# check if data folder exists 
if os.path.isdir("data"):
    if os.path.isfile("data/data.db"):
        #log success
        pass
    else:
        # change current directory to data folder
        os.chdir("data")
        # create data.db file in data folder
        f=open("data.db","w")
        f.close()
        os.chdir("../")
else:
    # create data directory
    os.mkdir("data")
    # create data.db file in data folder
    f=open("data/data.db","r")
    f.close()
# create tables in data.db
