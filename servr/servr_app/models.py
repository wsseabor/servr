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

"""
SQLite3 model class, handles data storage with persistence
"""
class SQLModel:

    """
    @param self.conn - connection to database using SQlite3
    @param self.cur - cursor object used to send SQL commands to database
    """
    
    def __init__(self, db):
        self.conn = sql.connect(db)
        self.cur = self.conn.cursor()

    """
    Create a table in chosen database
    @param table_name - name of table
    @param fields - dictionary of fields with required data types for population
    """
    def create_table(self, table_name, fields):
        self.fields = {
        "Date": {'req': True, 'type': ft.isoDateString},
        "Tips": {'req': True, 'type': ft.decimal},
        "Notes": {'req': False, 'type': ft.longString}
    }
        
        fields_str = ', '.join(f'{k} {v}' for k, v in self.fields.items)
        
        self.cur.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({fields_str})')

        self.conn.commit()
