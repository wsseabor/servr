import csv
from pathlib import Path
from datetime import datetime
import os

from .constants import FieldTypes as ft

class CSVModel:
    fields = {
        "Date": {'req' : True, 'type' : ft.isoDateString},
        "Tips" : {'req' : True, 'type' : ft.decimal},
        "Notes" : {'req' : False, 'type' : ft.longString}
    }

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

    def saveRecord(self, data):
        newfile = not self.file.exists()

        with open(self.file, 'a', newline='') as f:
            csvwriter = csv.DictWriter(f, fieldnames=self.fields.keys())
            if newfile:
                csvwriter.writeheader()
            
            csvwriter.writerow(data)