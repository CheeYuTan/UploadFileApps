from dash import html, dcc
import dash_bootstrap_components as dbc
from components.data_table import get_data_table

def get_table_selection_section():
    return dbc.Row([
        dbc.Col([
            html.H5("Select Target Table", className="fw-bold mt-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Catalog"),
                    dcc.Dropdown(id="catalog-select", placeholder="Select a catalog")
                ], width=4),
                dbc.Col([
                    dbc.Label("Schema"),
                    dcc.Dropdown(id="schema-select", placeholder="Select a schema", disabled=True)
                ], width=4),
                dbc.Col([
                    dbc.Label("Table"),
                    dcc.Dropdown(id="table-select", placeholder="Select a table", disabled=True)
                ], width=4),
            ]),
            # Add table preview section
            html.Div([
                html.H6("Table Preview", className="mt-4"),
                html.Div(id="table-preview-metadata", className="text-muted mb-2"),
                dcc.Loading(
                    id="loading-table-preview",
                    type="circle",
                    children=get_data_table("table-preview")
                )
            ], id="table-preview-section", style={"display": "none"}),
        ])
    ]) 