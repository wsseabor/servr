import tkinter as tk
from tkinter import ttk
from datetime import datetime

from . import widgets as w
from .constants import FieldTypes as ft

class DataRecordForm(ttk.Frame):

    var_types = {
        ft.string: tk.StringVar,
        ft.isoDateString: tk.StringVar,
        ft.longString: tk.StringVar,
        ft.decimal: tk.DoubleVar,
        ft.integer: tk.IntVar
    }

    def _addFrame(self, label, cols=3):
        frame = ttk.LabelFrame(self, text=label)
        frame.grid(sticky=tk.W + tk.E)
        for i in range(cols):
            frame.columnconfigure(i, weight = 1)
        return frame

    def __init__(self, parent, model, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.model = model
        fields = self.model.fields

        self._vars = {
            key: self.var_types[spec['type']]()
            for key, spec in fields.items()
        }

        self.columnconfigure(0, weight = 1)

        rInfo = self._addFrame("Shift Information")

        minTipsVar = tk.DoubleVar(value='-infinity')
        maxTipsVar = tk.DoubleVar(value='infinity')

        w.LabelInput(rInfo, 'Date', fieldSpec=fields['Date'], var=self._vars['Date']).grid(row=0, column=0)
        w.LabelInput(rInfo, 'Tips', fieldSpec=fields['Tips'], var=self._vars['Tips'], inputArgs={"min": minTipsVar, "max": maxTipsVar}).grid(row=0, column=1)
        w.LabelInput(self, "Notes", fieldSpec=fields['Notes'], var=self._vars['Notes'], inputArgs={"width": 75, "height": 10}).grid(sticky=(tk.W + tk.E), row=3, column=0)
        
        buttons = tk.Frame(self)
        buttons.grid(sticky=tk.W + tk.E, row=4)
        self.saveButton = ttk.Button(buttons, text="Save", command=self._on_save)
        self.saveButton.pack(side=tk.RIGHT)

        self.resetButton = ttk.Button(buttons, text="Reset", command=self.reset)
        self.resetButton.pack(side= tk.RIGHT)

    def reset(self):
        for var in self._vars.values():
            if isinstance(var, tk.BooleanVar):
                var.set(False)
            else:
                var.set('')

    def get(self):
        data = dict()

        for key, variable in self._vars.items():
            try:
                data[key] = variable.get()
            except tk.TclError:
                message = f'Error in field {key}. Data not saved.'
                raise ValueError(message)

        return data

    def _on_save(self):
        self.event_generate('<<SaveRecord>>')

    def get_errors(self):
        errors = dict()

        