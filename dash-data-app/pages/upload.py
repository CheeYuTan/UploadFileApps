import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
from dbutils import save_file_to_volume
from config import DATABRICKS_VOLUME_PATH
from typing import Tuple, Optional
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path="/")

layout = dbc.Container([
    html.H4("Append Table From File Upload", className="fw-bold mt-4 text-center"),

    # Add loading overlay for the entire upload process
    dbc.Spinner(
        html.Div(id="upload-progress", className="text-center mb-3"),
        color="primary",
        type="border",
    ),

    dcc.Upload(
        id="file-upload",
        children=html.Div([
            html.Img(src="/assets/upload-icon.png", className="upload-icon"),
            html.P("Drop a file here, or browse your local system", className="text-muted text-center"),
            html.P("Supported file formats: .csv, .tsv", className="text-muted small text-center")
        ]),
        style={
            "border": "2px dashed #ddd",
            "padding": "40px",
            "text-align": "center",
            "border-radius": "10px",
            "background-color": "#f8f9fa",
            "cursor": "pointer"
        },
        multiple=False
    ),

    html.Div(id="upload-status", className="mt-4 text-center"),
    dcc.Location(id="redirect", refresh=True),
    dcc.Store(id="file-path", storage_type="session")
], fluid=True)

@callback(
    [Output("redirect", "pathname"),
     Output("upload-status", "children"),
     Output("file-path", "data"),
     Output("upload-progress", "children")],
    Input("file-upload", "contents"),
    State("file-upload", "filename"),
    prevent_initial_call=True
)
def handle_file_upload(
    contents: Optional[str], 
    filename: Optional[str]
) -> Tuple[str, html.P, Optional[str], str]:
    """Handle file upload and validation.
    
    Args:
        contents: Base64 encoded file contents
        filename: Original filename
        
    Returns:
        Tuple containing:
        - Redirect path
        - Status message component
        - File path for storage
        - Progress message
    """
    if contents is None or filename is None:
        raise PreventUpdate

    # Validate file size (100MB limit)
    file_size = len(contents) * 3/4  # Approximate size from base64
    if file_size > 100 * 1024 * 1024:
        return (
            "/",
            html.P("File too large. Maximum size is 100MB.", className="text-danger"),
            None,
            ""
        )

    # Validate file extension
    if not filename.lower().endswith(('.csv', '.tsv')):
        return (
            "/",
            html.P("Invalid file format. Please upload a CSV or TSV file.", className="text-danger"),
            None,
            ""
        )

    try:
        # Show upload in progress message
        progress_message = html.Div([
            "Uploading and processing file...",
            html.Div(className="mt-2"),
            dbc.Progress(value=100, striped=True, animated=True)
        ])

        file_path = save_file_to_volume(contents, DATABRICKS_VOLUME_PATH, filename)
        if file_path:
            return (
                "/append-table",
                html.P(f"File uploaded successfully: {filename}", className="text-success"),
                file_path,
                ""
            )
        
        return (
            "/",
            html.P("Failed to upload file. Please try again.", className="text-danger"),
            None,
            ""
        )

    except Exception as e:
        return (
            "/",
            html.P(f"Error: {str(e)}", className="text-danger"),
            None,
            ""
        )