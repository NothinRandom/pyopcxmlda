from .constants import DataType
from typing import Union


def cast_data(value: Union[str, list], data_type: str):
    data_formatted = None
    if DataType.BOOL in data_type:
        data_formatted = True if "true" in value else False
    elif (
        DataType.BYTE in data_type
        or DataType.UBYTE in data_type
        or DataType.SHORT in data_type
        or DataType.USHORT in data_type
        or DataType.INT in data_type
        or DataType.UINT in data_type
        or DataType.LONG in data_type
        or DataType.ULONG in data_type
    ):
        data_formatted = int(value)
    elif (
        DataType.FLOAT in data_type
        or DataType.DOUBLE in data_type
        or DataType.DECIMAL in data_type
    ):
        data_formatted = float(value)
    elif DataType.ARRAY in data_type:
        data_type = data_type.lower()
        if (
            DataType.FLOAT in data_type
            or DataType.DOUBLE in data_type
            or DataType.DECIMAL in data_type
        ):
            data_formatted = [float(x) for x in value]
        elif (
            DataType.BYTE in data_type
            or DataType.UBYTE in data_type
            or DataType.SHORT in data_type
            or DataType.USHORT in data_type
            or DataType.INT in data_type
            or DataType.UINT in data_type
            or DataType.LONG in data_type
            or DataType.ULONG in data_type
        ):
            data_formatted = [int(x) for x in value]
        elif DataType.BOOL in data_type:
            data_formatted = [True if "true" in x else False for x in value]
        else:
            data_formatted = value
    else:
        data_formatted = value
    
    return data_formatted
