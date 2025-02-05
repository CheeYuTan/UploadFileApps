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
                # Loading spinner for append operation
                dbc.Spinner(
                    html.Div(id="loading-append"),
                    color="primary",
                    type="border",
                    fullscreen=True,  # Makes it center on screen
                    fullscreen_style={"backgroundColor": "rgba(0, 0, 0, 0.3)"}  # Semi-transparent overlay
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
                        html.I(className="bi bi-cloud-upload me-2"),  # Upload icon
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