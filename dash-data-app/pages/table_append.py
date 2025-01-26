import dash
import dash_bootstrap_components as dbc
import dash.dash_table as dt
from dash import html, dcc, callback, Input, Output, State
from dbutils import read_file_from_volume
from config import DATABRICKS_VOLUME_PATH

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

    dbc.Modal([
        dbc.ModalHeader("Advanced Attributes"),
        dbc.ModalBody([
            dbc.Label("Column delimiter"),
            dcc.Dropdown(
                id="column-delimiter",
                options=[
                    { "label": "Comma (,)", "value": "," },
                    { "label": "Semicolon (;)", "value": ";" },
                    { "label": "Pipe (|)", "value": "|" }
                ],
                value=",",
                clearable=False
            ),

            dbc.Label("Escape character"),
            dcc.Dropdown(
                id="escape-character",
                options=[
                    { "label": 'Double Quote (")', "value": '"' },
                    { "label": "Single Quote (')", "value": "'" }
                ],
                value='"',
                clearable=False
            ),

            dbc.Checkbox(
                id="first-row-header",
                label="First row contains header",
                value=True
            ),
        ]),
        dbc.ModalFooter(
            dbc.Button("Save", id="save-advanced-attributes", color="success", className="ms-auto")
        )
    ], id="advanced-attributes-modal", is_open=False),

    dbc.Button("Confirm and Append Data", id="confirm-append", color="success", className="mt-3"),

    dcc.Store(id="file-path", storage_type="session"),
    dcc.Store(id="csv-settings", storage_type="session")
], fluid=True)


@callback(
    Output("advanced-attributes-modal", "is_open"),
    Input("advanced-attributes-btn", "n_clicks"),
    [State("advanced-attributes-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_advanced_attributes(n_clicks, is_open):
    return not is_open


@callback(
    Output("csv-settings", "data"),
    Input("save-advanced-attributes", "n_clicks"),
    [
        State("column-delimiter", "value"),
        State("escape-character", "value"),
        State("first-row-header", "value")
    ],
    prevent_initial_call=True
)
def save_csv_settings(n_clicks, delimiter, escape_char, header):
    return {
        "delimiter": delimiter,
        "escape_char": escape_char,
        "header": 0 if header else None
    }


@callback(
    [Output("file-preview", "data"),
     Output("file-preview", "columns"),
     Output("file-info", "children")],
    Input("file-path", "data"),
    State("csv-settings", "data"),
    prevent_initial_call=True
)
def show_file_preview(file_path, csv_settings):
    if not file_path:
        return [], [], "No file available for preview."

    filename = file_path.split("/")[-1]
    delimiter = csv_settings.get("delimiter", ",")
    escape_char = csv_settings.get("escape_char", '"')
    header = csv_settings.get("header", 0)

    try:
        df = read_file_from_volume(DATABRICKS_VOLUME_PATH, filename, delimiter, escape_char, header)

        if not df.empty:
            columns = [{"name": col, "id": col} for col in df.columns]
            data = df.to_dict("records")
            return data[:10], columns, f"File retrieved: {filename}"
        else:
            return [], [], "File not found or error processing file."
    except Exception as e:
        return [], [], f"Error processing file: {str(e)}"