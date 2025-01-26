import dash_bootstrap_components as dbc
from dash import html, dcc

def get_csv_settings_modal():
    return dbc.Modal([
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
    ], id="advanced-attributes-modal", is_open=False) 