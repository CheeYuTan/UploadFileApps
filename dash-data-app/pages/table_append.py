import dash
import dash_bootstrap_components as dbc
import dash.dash_table as dt
from dash import html, dcc, callback, Input, Output, State
from dbutils import read_file_from_volume
from config import DATABRICKS_VOLUME_PATH
from components.csv_settings import get_csv_settings_modal

dash.register_page(__name__, path="/append-table")

layout = dbc.Container([
    html.H4("Append Table From File Upload", className="fw-bold mt-4"),

    dbc.Button("← Back", id="back-button", href="/", color="secondary", outline=True, className="mb-3"),

    # Add loading overlay for the entire process
    dbc.Spinner(
        html.Div(id="processing-status", className="mt-3"),
        color="primary",
        type="border",
    ),

    # File processing info with spinner
    dcc.Loading(
        id="loading-file-info",
        type="circle",
        children=html.Div([
            html.Div(id="file-info", className="mb-3 fw-bold"),
            html.Div(id="processing-message", className="text-info")
        ]),
    ),

    html.H5("File Preview", className="fw-bold mt-4"),
    dcc.Loading(
        id="loading-preview",
        type="circle",
        children=dt.DataTable(id="file-preview", style_table={"width": "100%"})
    ),

    dbc.Button("Advanced Attributes", id="advanced-attributes-btn", color="primary", className="mt-3"),

    get_csv_settings_modal(),

    dbc.Button("Confirm and Append Data", id="confirm-append", color="success", className="mt-3"),

    dcc.Store(id="file-path", storage_type="session"),
    dcc.Store(id="csv-settings", storage_type="session")
], fluid=True)


@callback(
    Output("advanced-attributes-modal", "is_open"),
    [Input("advanced-attributes-btn", "n_clicks"),
     Input("close-modal", "n_clicks")],
    [State("advanced-attributes-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_advanced_attributes(open_clicks, close_clicks, is_open):
    if open_clicks or close_clicks:
        return not is_open
    return is_open


@callback(
    [Output("file-preview", "data"),
     Output("file-preview", "columns"),
     Output("file-info", "children")],
    [Input("file-path", "data"),
     Input("column-delimiter", "value"),
     Input("quote-character", "value"),
     Input("escape-character", "value"),
     Input("header-settings", "value"),
     Input("file-encoding", "value")],
    prevent_initial_call=True
)
def show_file_preview(file_path, delimiter, quote_char, escape_char, header, encoding):
    """Update preview whenever file path or any CSV setting changes"""
    if not file_path:
        return [], [], "No file available for preview."

    # Create settings dict from current values
    csv_settings = {
        "delimiter": delimiter or ",",
        "quote_char": quote_char or '"',
        "escape_char": escape_char or '"',
        "header": header if header is not None else 0,
        "encoding": encoding or "utf-8"
    }

    filename = file_path.split("/")[-1]
    try:
        df = read_file_from_volume(
            DATABRICKS_VOLUME_PATH, 
            filename, 
            delimiter=csv_settings["delimiter"],
            escape_char=csv_settings["escape_char"],
            header=csv_settings["header"],
            encoding=csv_settings["encoding"],
            limit=10
        )

        if not df.empty:
            columns = [{"name": col, "id": col} for col in df.columns]
            data = df.to_dict("records")
            return data, columns, f"File retrieved: {filename}"
        else:
            return [], [], "File not found or error processing file."
    except Exception as e:
        return [], [], f"Error processing file: {str(e)}"