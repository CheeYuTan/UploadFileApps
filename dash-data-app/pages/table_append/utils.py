from typing import Dict, Optional
import pandas as pd

def get_data_type_icon(data_type: str) -> Dict[str, str]:
    """Returns the appropriate icon path for a given data type"""
    data_type = data_type.upper()
    
    icon_path = "assets/data-types/"
    
    if data_type in ['TINYINT', 'SMALLINT', 'INT', 'BIGINT']:
        return {"src": icon_path + "Integral_Numeric.png"}
    elif data_type in ['BINARY']:
        return {"src": icon_path + "Binary.png"}
    elif data_type in ['BOOLEAN']:
        return {"src": icon_path + "Boolean.png"}
    elif data_type in ['ARRAY', 'MAP', 'STRUCT', 'VARIANT', 'OBJECT']:
        return {"src": icon_path + "Complex.png"}
    elif data_type in ['DATE']:
        return {"src": icon_path + "Date.png"}
    elif data_type in ['TIMESTAMP', 'TIMESTAMP_NTZ']:
        return {"src": icon_path + "Datetime.png"}
    elif data_type in ['DECIMAL']:
        return {"src": icon_path + "Decimal.png"}
    elif data_type in ['FLOAT', 'DOUBLE']:
        return {"src": icon_path + "Float.png"}
    elif data_type in ['STRING']:
        return {"src": icon_path + "String.png"}
    else:
        return None

def infer_column_type(series: pd.Series) -> str:
    """Infers the data type of a pandas Series"""
    sample_values = series.dropna()
    if len(sample_values) > 0:
        if pd.api.types.is_numeric_dtype(sample_values):
            return "FLOAT" if all(sample_values.astype(str).str.contains('\.').fillna(False)) else "INT"
        elif pd.api.types.is_datetime64_any_dtype(sample_values):
            return "TIMESTAMP"
        elif pd.api.types.is_bool_dtype(sample_values):
            return "BOOLEAN"
    return "STRING"

def create_header_conditional(col: str, icon_path: Optional[str]) -> Dict:
    """Creates header conditional styling for a column"""
    if not icon_path:
        return {}
    return {
        'if': {'column_id': col},
        'backgroundImage': f'url({icon_path})',
        'backgroundRepeat': 'no-repeat',
        'backgroundPosition': '4px center',
        'backgroundSize': '20px',
        'paddingLeft': '28px'
    } 