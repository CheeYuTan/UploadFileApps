from dash import callback, Input, Output
import pandas as pd
from dbutils import read_file_from_volume
from config import DATABRICKS_VOLUME_PATH

@callback(
    [Output("file-preview", "data"),
     Output("file-preview", "columns"),
     Output("file-info", "children"),
     Output("file-preview-metadata", "children")],
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
        return [], [], "No file available for preview.", ""

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
            
            # Convert all data to strings to avoid type issues
            df = df.astype(str)
            
            # Create simple columns
            columns = [{"name": col, "id": col} for col in df.columns]
            
            preview_metadata = f"Showing {len(df)} rows, {len(df.columns)} columns"
            return (
                df.to_dict("records"),
                columns,
                f"File retrieved: {filename}",
                preview_metadata
            )
        else:
            return [], [], "File not found or error processing file.", ""
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return [], [], f"Error processing file: {str(e)}", "" 