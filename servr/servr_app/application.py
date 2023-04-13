import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from . import views as v
from . import models as m

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = m.CSVModel()

        self.title("Servr 0.01")
        self.columnconfigure(0, weight=1)

        ttk.Label(
            self, text="Servr App 0.01", font=("TkDefaultFont", 16)
        ).grid(row=0)

        self.recordForm = v.DataRecordForm(self, self.model)
        self.recordForm.grid(row=1, padx=10, sticky=(tk.W + tk.E))
        self.recordForm.bind('<<SaveRecord>>', self._on_save)

        self.status = tk.StringVar()
        self.statusBar = ttk.Label(self, textvariable=self.status).grid(sticky=(tk.W + tk.E), row=2, padx=10)

        self.recordsSaved = 0

    def _on_save(self, *_):
        errors = self.recordForm.get_errors()
        if errors:
            message = "Cannot save record."
            detail = (
                "The following fields have errors: "
                "\n * {}".format(
                    '\n * '.join(errors.keys())
                )
            )

            messagebox.showerror(
                title = 'Error',
                message = message,
                detail = detail
            )

            return False

        data = self.recordForm.get()
        self.model.saveRecord(data)
        self.recordsSaved += 1
        self.status.set(
            f"{self.recordsSaved} records saved this session."
        )
        self.recordForm.reset()