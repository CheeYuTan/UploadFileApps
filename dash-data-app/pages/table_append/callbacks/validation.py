from dash import callback, Input, Output, State, html
import pandas as pd
from dbutils import describe_table, read_file_from_volume
from config import DATABRICKS_VOLUME_PATH

@callback(
    [Output("validation-results", "children"),
     Output("confirm-append", "disabled")],
    Input("validate-data", "n_clicks"),
    [State("file-path", "data"),
     State("catalog-select", "value"),
     State("schema-select", "value"),
     State("table-select", "value"),
     State("column-delimiter", "value"),
     State("quote-character", "value"),
     State("escape-character", "value"),
     State("header-settings", "value"),
     State("file-encoding", "value")],
    prevent_initial_call=True
)
def validate_data(n_clicks, file_path, catalog, schema, table, delimiter, quote_char, escape_char, header, encoding):
    # ...
    csv_settings = {
        "delimiter": delimiter or ",",
        "quote_char": quote_char or '"',
        # Remove escape_char
        "header": header if header is not None else True,
        "encoding": encoding or "utf-8"
    }
    
    df = read_file_from_volume(
        DATABRICKS_VOLUME_PATH,
        file_path.split("/")[-1],
        delimiter=csv_settings["delimiter"],
        quote_char=csv_settings["quote_char"],
        header=csv_settings["header"],
        encoding=csv_settings["encoding"]
    )
    # ...

@callback(
    Output("processing-status", "children"),
    Input("confirm-append", "n_clicks"),
    [State("file-path", "data"),
     State("catalog-select", "value"),
     State("schema-select", "value"),
     State("table-select", "value"),
     State("column-delimiter", "value"),
     State("quote-character", "value"),
     State("escape-character", "value"),
     State("header-settings", "value"),
     State("file-encoding", "value")],
    prevent_initial_call=True
)
def append_data(n_clicks, file_path, catalog, schema, table, delimiter, quote_char, escape_char, header, encoding):
    # ... (existing append_data code) ... 