from dash import html
import dash_bootstrap_components as dbc

def get_validation_section():
    return html.Div([
        html.Div([
            dbc.Button(
                "Validate Data", 
                id="validate-data", 
                color="primary", 
                className="me-2",
                disabled=True  # Initially disabled
            ),
            dbc.Button(
                "Confirm and Append Data", 
                id="confirm-append", 
                color="success", 
                className="mt-3",
                disabled=True  # Initially disabled
            ),
        ], className="mt-3"),
        html.Div(id="validation-results", className="mt-3")
    ]) 