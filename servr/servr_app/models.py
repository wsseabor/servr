import csv
from pathlib import Path
from datetime import datetime
import os
import sqlite3 as sql

from .constants import FieldTypes as ft

#Model class that handles data storage / retrieval for our CSV format
class CSVModel:

    #Relevant fields we need to pull from our field type enum
    fields = {
        "Date": {'req' : True, 'type' : ft.isoDateString},
        "Tips" : {'req' : True, 'type' : ft.decimal, 'min' : 0, 'max' : 5000, 'inc' : .01},
        "Notes" : {'req' : False, 'type' : ft.longString}
    }

    #On initialization, handles file logic with error catching
    def __init__(self):
        datestring = datetime.today().strftime("%Y-%m-%d")
        filename = "servr_app_record_{}.csv".format(datestring)
        self.file = Path(filename)

        fileExists = os.access(self.file, os.F_OK)
        parentWritable = os.access(self.file.parent, os.W_OK)
        fileWritable = os.access(self.file, os.W_OK)

        if ((not fileExists and not parentWritable) or (fileExists and not fileWritable)):
            msg = f'Permission access denied using {filename}.'
            raise PermissionError(msg)

    #Handles save logic
    def saveRecord(self, data):
        newfile = not self.file.exists()

        with open(self.file, 'a', newline='') as f:
            csvwriter = csv.DictWriter(f, fieldnames=self.fields.keys())
            if newfile:
                csvwriter.writeheader()
            
            csvwriter.writerow(data)

class SQLModel:
    fields = {
        "Date": {'req': True, 'type': ft.isoDateString},
        "Tips": {'req': True, 'type': ft.decimal},
        "Notes": {'req': False, 'type': ft.longString}
    }

    record_insert_query = (
        'INSERT INTO tip_records VALUES (%(Date)s, %(Tips)s, %(Note)s)' 
    )

    def __init__(self, host, db, user, pw):
        self.conn = sql.connect(db)