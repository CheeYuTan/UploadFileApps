import dash_bootstrap_components as dbc
from dash import html, dcc
from components.csv_settings import get_csv_settings_modal
from .data_preview import get_file_preview_section
from .table_selection import get_table_selection_section

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
        
        # Action buttons
        dbc.Button("Confirm and Append Data", id="confirm-append", color="success", className="mt-3"),
        
        # Storage
        dcc.Store(id="file-path", storage_type="session"),
        dcc.Store(id="csv-settings", storage_type="session")
    ], fluid=True) 