from enum import Enum, auto

class FieldTypes(Enum):
    string = auto()
    stringList = auto()
    shortStringList = auto()
    isoDateString = auto()
    longString = auto()
    decimal = auto()
    integer = auto()
    boolean = auto()