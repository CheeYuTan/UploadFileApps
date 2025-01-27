from dash import html, dcc
import dash_bootstrap_components as dbc
from components.data_table import get_data_table

def get_file_preview_section():
    return html.Div([
        html.H5("File Preview", className="fw-bold mt-4"),
        html.Div(id="file-preview-metadata", className="text-muted small mb-2"),
        dcc.Loading(
            id="loading-preview",
            type="circle",
            children=get_data_table("file-preview")
        )
    ]) 