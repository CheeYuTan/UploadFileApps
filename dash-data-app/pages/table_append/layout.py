import dash_bootstrap_components as dbc
from dash import html, dcc
from .components.file_preview import get_file_preview_section
from .components.table_selection import get_table_selection_section
from .components.validation import get_validation_section
from components.csv_settings import get_csv_settings_modal

def get_layout():
    return dbc.Container([
        html.H4("Append Table From File Upload", className="fw-bold mt-4"),
        dbc.Button("← Back", id="back-button", href="/", color="secondary", outline=True, className="mb-3"),
        
        # Processing status
        dbc.Spinner(
            html.Div(id="processing-status", className="mt-3"),
            color="primary",
            type="border",
        ),
        
        # File preview section
        get_file_preview_section(),
        
        # CSV settings
        dbc.Button("Advanced Attributes", id="advanced-attributes-btn", color="primary", className="mt-3"),
        get_csv_settings_modal(),
        
        # Table selection section
        get_table_selection_section(),
        
        # Validation section
        get_validation_section(),
        
        # Add loading spinner and status alert
        dbc.Row([
            dbc.Col([
                # Loading overlay with spinner
                html.Div(
                    dbc.Spinner(size="lg", color="primary"),
                    id="loading-overlay",
                    style={
                        "position": "fixed",
                        "top": 0,
                        "left": 0,
                        "right": 0,
                        "bottom": 0,
                        "display": "none",  # Initially hidden
                        "alignItems": "center",
                        "justifyContent": "center",
                        "backgroundColor": "rgba(0, 0, 0, 0.5)",  # Semi-transparent background
                        "zIndex": 1050  # Above other content
                    }
                ),
                # Status alert for success/error messages
                dbc.Collapse(
                    id="append-status",
                    is_open=False,
                    className="mt-3"
                )
            ])
        ]),
        
        # Confirm append button
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [
                        html.I(className="bi bi-cloud-upload me-2"),
                        "Confirm and Append Data"
                    ],
                    id="confirm-append",
                    color="primary",
                    className="mt-3",
                    disabled=False
                )
            ], className="text-center")
        ]),
        
        # Storage
        dcc.Store(id="file-path", storage_type="session"),
        dcc.Store(id="csv-settings", storage_type="session")
    ], fluid=True) 