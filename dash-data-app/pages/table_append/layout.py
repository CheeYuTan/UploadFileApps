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
        
        # Storage
        dcc.Store(id="file-path", storage_type="session"),
        dcc.Store(id="csv-settings", storage_type="session")
    ], fluid=True) 