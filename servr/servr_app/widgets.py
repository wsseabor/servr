import tkinter as tk
from tkinter import ttk
from datetime import datetime
from decimal import Decimal, InvalidOperation
from .constants import FieldTypes as ft

""" Mixin class allowing input validation in subclasses """
class ValidatedMixin:
    def __init__(self, *args, error_var=None, **kwargs):

        """ Set an error message if none is passed """
        self.error_var = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)

        """ Registering instance methods for valid / invalid commands """
        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)

        """ Sets substitution codes for validation """
        self.configure(
            validate='all',
            validatecommand = (vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
            invalidcommand= (invcmd, '%P', '%s', '%S', '%V', '%i', '%d')
        )

    """ Error condition handler, sets text to red as warning """
    def _toggle_error(self, on=False):
        self.configure(foreground = ('red' if on else 'black'))

    """ Protected callback validation, rather like abtract class methods in Java """
    def _validate(self, proposed, current, char, event, index, action):
        self.error.set('')
        self._toggle_error()
        valid = True

        state = str(self.configure('state')[-1])
        if state == tk.DISABLED:
            return valid

        if event == 'focusout':
            valid = self._focusout_validate(event=event)
        elif event == 'key':
            valid = self._key_validate(
                proposed = proposed,
                current = current,
                char = char,
                event = event,
                index = index,
                action = action
            )

        return valid

    """ Instance methods that subclasses will override in validation fails """
    def _focusout_validate(self, **kwargs):
        return True

    """ Same as above """
    def _key_validate(self, **kwargs):
        return True

    """ Protected callback for invalid data, no return value to set a valid flag, do nothing by default"""
    def _invalid(self, proposed, current, char, event, index, action):
        if event == 'focusout':
            self._focusout_invalid(event=event)

        elif event == 'key':
            self._key_invalid(
                proposed = proposed,
                current = current,
                char = char,
                event = event,
                index = index,
                action = action
            )

    """ Handles invalid data with focus out or key events """
    def _focusout_invalid(self, **kwargs):
        self._toggle_error(True)

    def _key_invalid(self, **kwargs):
        pass

    """ Run validation, if fails, manually execute the focusout event """
    def trigger_focusout_validation(self):
        valid = self._validate('', '', '', 'focusout', '', '')

        if not valid:
            self._focusout_invalid(event='focusout')
        
        return valid

class DateEntry(ValidatedMixin, ttk.Entry):

    def _key_validate(self, action, index, char, **kwargs):
        valid = True

        if action == '0':
            valid = True
        elif index in ('0', '1', '2', '3', '5', '6', '8', '9'):
            valid = char.isdigit()
        elif index in ('4', '7'):
            valid = char == '-'
        else:
            valid = False

        return valid

    def _focusout_validate(self, event):
        valid = True

        if not self.get():
            self.error.set('A value is required.')
            valid = False

        try:
            datetime.strptime(self.get(), '%Y-%m-%d')
        except ValueError:
            self.error.set('Invalid date.')
            valid = False

        return valid

class ValidatedSpinbox(ValidatedMixin, ttk.Spinbox):
    def __init__(self, *args, from_="-Infinity", to="Infinity", **kwargs):
        super().__init__(*args, from_=from_, to=to, **kwargs)
        increment = Decimal(str(kwargs.get('increment', '1.0')))
        self.precision = increment.normalize().as_tuple().exponent

    def _key_validate(self, char, index, current, proposed, action, **kwargs):
        if action == '0':
            return True
        valid = True
        minVal = self.cget('from')
        maxVal = self.cget('to')
        noNegative = minVal >= 0
        noDecimal = self.precision >= 0

        if any([
            (char not in '-1234567890.'),
            (char == '-' and (noNegative or index != '0')),
            (char == '.' and (noDecimal or '.' in current))
        ]):
            return False

        if proposed in '-.':
            return True

        proposed = Decimal(proposed)
        proposedPrecision = proposed.as_tuple().exponent

        if any([
            (proposed > maxVal),
            (proposedPrecision < self.precision)
        ]):
            return False

        return valid

    def _focusout_validate(self, **kwargs):
        valid = True
        value = self.get()
        minVal = self.cget('from')
        maxVal = self.cget('to')

        try:
            dValue = Decimal(value)
        except InvalidOperation:
            self.error.set(f'Invalid number string: {value}')
            return False
        
        if dValue < minVal:
            self.error.set(f'Value is too low (min {minVal}')
            valid = False
        
        if dValue > maxVal:
            self.error.set(f'Value is too high (max {maxVal}')
            valid = False

        return valid

class BoundText(tk.Text):
    def __init__(self, *args, textvariable=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._variable = textvariable

        if self._variable:
            self.insert('1.0', self._variable.get())
            self._variable.trace_add('write', self._set_content)
            self.bind('<<Modified>>', self._set_var)

    def _set_content(self, *_):
        self.delete('1.0', tk.END)
        self.insert('1.0', self._variable.get())

    def _set_var(self, *_):
        if self.edit_modified():
            content = self.get('1.0', 'end-1chars')
            self._variable.set(content)
            self.edit_modified(False)

class LabelInput(tk.Frame):
    fieldTypes = {
        ft.string: tk.StringVar,
        ft.isoDateString: DateEntry,
        ft.longString: BoundText,
        ft.decimal: ValidatedSpinbox,
        ft.integer: ValidatedSpinbox
    }

    def __init__(self, parent, label, var, inputClass=None, inputArgs=None, labelArgs=None, fieldSpec = None, disableVar = None, **kwargs):
        super().__init__(parent, **kwargs)
        inputArgs = inputArgs or {}
        labelArgs = labelArgs or {}
        self.variable = var
        self.variable.label_widget = self

        if fieldSpec:
            fieldType = fieldSpec.get('Type', ft.string)
            inputClass = inputClass or self.fieldTypes.get(fieldType)

            if 'min' in fieldSpec and 'from_' not in inputArgs:
                inputArgs['from_'] = fieldSpec.get('min')
            if 'max' in fieldSpec and 'to' not in inputArgs:
                inputArgs['to'] = fieldSpec.get('max')
            if 'inc' in fieldSpec and 'increment' not in inputArgs:
                inputArgs['increment'] = fieldSpec.get('inc')
            if 'values' in fieldSpec and 'values' not in inputArgs:
                inputArgs['values'] = fieldSpec.get('values')

        if inputClass in (ttk.Checkbutton, ttk.Button):
            inputArgs['text'] = label
        else:
            self.label = ttk.Label(self, text=label, **labelArgs)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))

        if inputClass in (ttk.Checkbutton, ttk.Button, ttk.Radiobutton):
            inputArgs['variable'] = self.variable
        else:
            inputArgs['textvariable'] = self.variable

        """
        if inputClass == ttk.Radiobutton:
            self.input = tk.Frame(self)
            for v in inputArgs.pop('values', []):
                button = ttk.Radiobutton(
                    self.input, value=v, text=v, **inputArgs
                )
                button.pack(
                    side=tk.LEFT, ipadx=10, ipady=2, expand=True, fill='x'
                )
        else:
            self.input = inputClass(self, **inputArgs)
        

        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
        self.columnconfigure(0, weight=1)
        """

    def grid(self, sticky=(tk.E + tk.W), **kwargs):
        super().grid(sticky=sticky, **kwargs)