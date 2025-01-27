import dash_bootstrap_components as dbc
from dash import html, dcc

def get_csv_settings_modal():
    return dbc.Modal([
        dbc.ModalHeader("CSV Settings"),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Column Delimiter"),
                    dbc.Input(id="column-delimiter", type="text", placeholder=",")
                ]),
                dbc.Col([
                    dbc.Label("Quote Character"),
                    dbc.Input(id="quote-character", type="text", placeholder='"')
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Header Settings"),
                    dbc.Select(
                        id="header-settings",
                        options=[
                            {"label": "First row is header", "value": "true"},
                            {"label": "No header", "value": "false"}
                        ],
                        value="true"
                    )
                ]),
                dbc.Col([
                    dbc.Label("File Encoding"),
                    dbc.Input(id="file-encoding", type="text", placeholder="utf-8")
                ])
            ], className="mt-3")
        ]),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-csv-settings", className="ms-auto")
        )
    ], id="csv-settings-modal", is_open=False) 