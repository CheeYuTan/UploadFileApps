import dash_bootstrap_components as dbc
from dash import html, dcc

def get_csv_settings_modal():
    return dbc.Modal([
        dbc.ModalHeader("CSV Import Settings"),
        dbc.ModalBody([
            # Delimiter settings
            dbc.Label("Column Delimiter"),
            dcc.Dropdown(
                id="column-delimiter",
                options=[
                    {"label": "Comma (,)", "value": ","},
                    {"label": "Semicolon (;)", "value": ";"},
                    {"label": "Tab (\\t)", "value": "\t"},
                    {"label": "Pipe (|)", "value": "|"},
                    {"label": "Space ( )", "value": " "}
                ],
                value=",",
                clearable=False,
                className="mb-3"
            ),

            # Quote character
            dbc.Label("Quote Character"),
            dcc.Dropdown(
                id="quote-character",
                options=[
                    {"label": 'Double Quote (")', "value": '"'},
                    {"label": "Single Quote (')", "value": "'"},
                    {"label": "None", "value": ""}
                ],
                value='"',
                clearable=False,
                className="mb-3"
            ),

            # Escape character
            dbc.Label("Escape Character"),
            dcc.Dropdown(
                id="escape-character",
                options=[
                    {"label": 'Backslash (\\)', "value": "\\"},
                    {"label": 'Double Quote (")', "value": '"'},
                    {"label": "None", "value": ""}
                ],
                value='"',
                clearable=False,
                className="mb-3"
            ),

            # Header settings
            dbc.Label("Header Settings"),
            dbc.RadioItems(
                id="header-settings",
                options=[
                    {"label": "First row as header", "value": 0},
                    {"label": "No header (auto-generate column names)", "value": None}
                ],
                value=0,
                className="mb-3"
            ),

            # Encoding
            dbc.Label("File Encoding"),
            dcc.Dropdown(
                id="file-encoding",
                options=[
                    {"label": "UTF-8", "value": "utf-8"},
                    {"label": "ASCII", "value": "ascii"},
                    {"label": "ISO-8859-1", "value": "iso-8859-1"},
                    {"label": "UTF-16", "value": "utf-16"}
                ],
                value="utf-8",
                clearable=False,
                className="mb-3"
            ),

            dbc.Alert(
                "Changes will be applied to the preview immediately",
                color="info",
                className="mt-3"
            )
        ]),
        dbc.ModalFooter(
            dbc.Button("Apply Settings", id="save-advanced-attributes", color="success", className="ms-auto")
        )
    ], id="advanced-attributes-modal", is_open=False) 