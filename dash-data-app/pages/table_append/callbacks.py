from dash import callback, Input, Output, State
from typing import Dict, List, Tuple, Optional
from .utils import get_data_type_icon, infer_column_type, create_header_conditional
from dbutils import (
    read_file_from_volume, 
    list_catalogs, 
    list_schemas, 
    list_tables,
    describe_table,
    get_sample_data
)
from config import DATABRICKS_VOLUME_PATH
import pandas as pd

@callback(
    [Output("table-preview", "data"),
     Output("table-preview", "columns"),
     Output("table-preview-metadata", "children"),
     Output("table-preview-section", "style"),
     Output("table-preview", "tooltip_header"),
     Output("table-preview", "style_header_conditional")],
    [Input("catalog-select", "value"),
     Input("schema-select", "value"),
     Input("table-select", "value")],
    background=True,
    running=[
        (Output("table-preview", "style"), {"opacity": "0.5"}, {"opacity": "1"}),
        (Output("confirm-append", "disabled"), True, False)
    ]
)
def update_table_preview(
    catalog: Optional[str], 
    schema: Optional[str], 
    table: Optional[str]
) -> Tuple[List[dict], List[dict], str, dict, dict, List[dict]]:
    if not all([catalog, schema, table]):
        return [], [], "", {"display": "none"}, {}, []
    
    try:
        # Get sample data and schema
        sample_df = get_sample_data(catalog, schema, table, limit=10)
        schema_df = describe_table(catalog, schema, table)
        data_types = dict(zip(schema_df['col_name'], schema_df['data_type']))
        
        # Create columns with tooltips
        columns = []
        tooltip_headers = {}
        header_conditionals = []
        
        for col in sample_df.columns:
            data_type = data_types.get(col, "").upper()
            icon = get_data_type_icon(data_type)
            icon_path = icon.get('src') if icon else None
            
            columns.append({
                "name": col,
                "id": col,
                "type": "numeric" if data_type in ["INT", "FLOAT", "DECIMAL"] else "text"
            })
            
            tooltip_headers[col] = {
                "value": f"Type: {data_type}",
                "type": "markdown"
            }
            
            if icon_path:
                header_conditionals.append(create_header_conditional(col, icon_path))
        
        return (
            sample_df.to_dict('records'),
            columns,
            f"Showing {len(sample_df)} sample rows",
            {"display": "block"},
            tooltip_headers,
            header_conditionals
        )
        
    except Exception as e:
        print(f"Error updating table preview: {str(e)}")
        return [], [], f"Error: {str(e)}", {"display": "none"}, {}, []

@callback(
    [Output("file-preview", "data"),
     Output("file-preview", "columns"),
     Output("file-info", "children"),
     Output("file-preview-metadata", "children"),
     Output("file-preview", "tooltip_header"),
     Output("file-preview", "style_header_conditional")],
    [Input("file-path", "data"),
     Input("column-delimiter", "value"),
     Input("quote-character", "value"),
     Input("escape-character", "value"),
     Input("header-settings", "value"),
     Input("file-encoding", "value")],
    prevent_initial_call=True
)
def show_file_preview(file_path, delimiter, quote_char, escape_char, header, encoding):
    if not file_path:
        return [], [], "No file available for preview.", "", {}, []

    csv_settings = {
        "delimiter": delimiter or ",",
        "quote_char": quote_char or '"',
        "escape_char": escape_char or '"',
        "header": header if header is not None else True,
        "encoding": encoding or "utf-8"
    }

    filename = file_path.split("/")[-1]
    try:
        df = read_file_from_volume(
            DATABRICKS_VOLUME_PATH, 
            filename, 
            delimiter=csv_settings["delimiter"],
            quote_char=csv_settings["quote_char"],
            header=csv_settings["header"],
            encoding=csv_settings["encoding"],
            limit=10
        )

        if not df.empty:
            if '_rescued_data' in df.columns:
                df = df.drop('_rescued_data', axis=1)
            
            # Create columns with inferred types
            columns = []
            tooltip_headers = {}
            header_conditionals = []
            
            # Create a dictionary of column data types
            data_types = {}
            for col in df.columns:
                # Infer data type from the column
                data_types[col] = infer_column_type(df[col])
            
            # Create columns and tooltips
            for col in df.columns:
                data_type = data_types[col]
                icon = get_data_type_icon(data_type)
                icon_path = icon.get('src') if icon else None
                
                columns.append({
                    "name": col,
                    "id": col,
                    "type": "numeric" if data_type in ["INT", "FLOAT", "DECIMAL"] else "text"
                })
                
                tooltip_headers[col] = {
                    "value": f"Type: {data_type}",
                    "type": "markdown"
                }
                
                if icon_path:
                    header_conditionals.append(create_header_conditional(col, icon_path))
            
            preview_metadata = f"Showing {len(df)} rows, {len(df.columns)} columns"
            return (
                df.to_dict("records"),
                columns,
                f"File retrieved: {filename}",
                preview_metadata,
                tooltip_headers,
                header_conditionals
            )
        else:
            return [], [], "File not found or error processing file.", "", {}, []
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return [], [], f"Error processing file: {str(e)}", "", {}, []

# Add catalog/schema/table selection callbacks
@callback(
    Output("catalog-select", "options"),
    Input("file-path", "data")
)
def load_catalogs(file_path):
    if not file_path:
        return []
    df = list_catalogs()
    return [{"label": catalog, "value": catalog} for catalog in df.iloc[:, 0].tolist()]

@callback(
    [Output("schema-select", "options"),
     Output("schema-select", "disabled")],
    Input("catalog-select", "value")
)
def load_schemas(catalog):
    if not catalog:
        return [], True
    df = list_schemas(catalog)
    return [{"label": schema, "value": schema} for schema in df.iloc[:, 0].tolist()], False

@callback(
    [Output("table-select", "options"),
     Output("table-select", "disabled")],
    [Input("catalog-select", "value"),
     Input("schema-select", "value")]
)
def load_tables(catalog, schema):
    if not catalog or not schema:
        return [], True
    df = list_tables(catalog, schema)
    return [{"label": table, "value": table} for table in df['tableName'].tolist()], False 