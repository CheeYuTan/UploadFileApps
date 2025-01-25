import dash_bootstrap_components as dbc
from dash import dcc, html

def get_layout():
    return dbc.Container([
        # Upload section
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div([
                            html.Img(src="/assets/upload-icon.png", className="upload-icon"),
                            html.H4("Upload file to append table", className="text-primary fw-bold mt-2"),
                            html.P("Upload tabular data files to append to an existing table."),
                        ], className="upload-box", id="upload-trigger", n_clicks=0),
                    ])
                ),
                width=6,
            )
        ], className="justify-content-center mt-5"),

        # Modal for selecting a table
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Table to Append Data To")),
            dbc.ModalBody([
                html.P("Only tables in Unity Catalog are available to select.", className="text-muted"),
                
                html.H6("All catalogs", className="text-muted mt-3"),

                # Dropdowns for catalog, schema, and table selection
                dcc.Dropdown(id="catalog-dropdown", placeholder="Select a catalog", className="dropdown mb-2"),
                dcc.Dropdown(id="schema-dropdown", placeholder="Select a schema", className="dropdown mb-2", disabled=True),
                dcc.Dropdown(id="table-dropdown", placeholder="Select a table", className="dropdown mb-2", disabled=True),

                html.Div(id="selected-table-path", className="mt-3 text-primary fw-bold"),
            ]),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal", className="ml-auto", color="secondary")
            ),
        ], id="table-selection-modal", is_open=False),

        html.Hr(),

        # Section to display schema and sample data
        dbc.Row([
            dbc.Col(html.H4("Table Schema", className="text-primary mt-4"), width=12),
            dbc.Col(dcc.Loading(dbc.Table(id="table-schema", bordered=True, hover=True, striped=True), type="circle"), width=12),
        ], className="mb-5"),

        dbc.Row([
            dbc.Col(html.H4("Sample Data", className="text-primary mt-4"), width=12),
            dbc.Col(dcc.Loading(dbc.Table(id="sample-data", bordered=True, hover=True, striped=True), type="circle"), width=12),
        ])
    ], fluid=True)