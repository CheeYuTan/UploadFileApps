import dash
import dash_bootstrap_components as dbc
import dash.dash_table as dt
from dash import html, dcc, callback, Input, Output, State
from dbutils import read_file_from_volume
from config import DATABRICKS_VOLUME_PATH
from components.csv_settings import get_csv_settings_modal

dash.register_page(__name__, path="/append-table")

layout = dbc.Container([
    html.H4("Append Table From File Upload", className="fw-bold mt-4"),

    dbc.Button("← Back", id="back-button", href="/", color="secondary", outline=True, className="mb-3"),

    # Add loading overlay for the entire process
    dbc.Spinner(
        html.Div(id="processing-status", className="mt-3"),
        color="primary",
        type="border",
    ),

    # File processing info with spinner
    dcc.Loading(
        id="loading-file-info",
        type="circle",
        children=html.Div([
            html.Div(id="file-info", className="mb-3 fw-bold"),
            html.Div(id="processing-message", className="text-info")
        ]),
    ),

    # Table selection section
    dbc.Row([
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
        ])
    ]),

    # File preview section with metadata
    dbc.Row([
        dbc.Col([
            html.H5("File Preview", className="fw-bold mt-4"),
            html.Div(id="preview-metadata", className="text-muted mb-2"),  # For row/column count
            dcc.Loading(
                id="loading-preview",
                type="circle",
                children=[
                    # Data type information
                    html.Div(id="datatype-info", className="mb-3"),
                    # Preview table
                    dt.DataTable(
                        id="file-preview",
                        style_table={"width": "100%"},
                        style_data_conditional=[{
                            'if': {'filter_query': '{value} = null'},
                            'backgroundColor': '#FFF3F3',
                            'color': '#FF0000'
                        }]
                    )
                ]
            )
        ])
    ]),

    dbc.Button("Advanced Attributes", id="advanced-attributes-btn", color="primary", className="mt-3"),

    get_csv_settings_modal(),

    dbc.Button("Confirm and Append Data", id="confirm-append", color="success", className="mt-3"),

    dcc.Store(id="file-path", storage_type="session"),
    dcc.Store(id="csv-settings", storage_type="session")
], fluid=True)


@callback(
    Output("advanced-attributes-modal", "is_open"),
    [Input("advanced-attributes-btn", "n_clicks"),
     Input("close-modal", "n_clicks")],
    [State("advanced-attributes-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_advanced_attributes(open_clicks, close_clicks, is_open):
    if open_clicks or close_clicks:
        return not is_open
    return is_open


@callback(
    Output("catalog-select", "options"),
    Input("file-path", "data")  # Trigger when file is uploaded
)
def load_catalogs(file_path):
    if not file_path:
        return []
    df = list_catalogs()
    return [{"label": catalog, "value": catalog} for catalog in df.iloc[:, 0].tolist()]

@callback(
    [Output("schema-select", "options"),
     Output("schema-select", "disabled")],
    Input("catalog-select", "value")
)
def load_schemas(catalog):
    if not catalog:
        return [], True
    df = list_schemas(catalog)
    return [{"label": schema, "value": schema} for schema in df.iloc[:, 0].tolist()], False

@callback(
    [Output("table-select", "options"),
     Output("table-select", "disabled")],
    [Input("catalog-select", "value"),
     Input("schema-select", "value")]
)
def load_tables(catalog, schema):
    if not catalog or not schema:
        return [], True
    df = list_tables(catalog, schema)
    return [{"label": table, "value": table} for table in df['tableName'].tolist()], False

@callback(
    [Output("file-preview", "data"),
     Output("file-preview", "columns"),
     Output("file-info", "children"),
     Output("preview-metadata", "children"),
     Output("datatype-info", "children")],
    [Input("file-path", "data"),
     Input("column-delimiter", "value"),
     Input("quote-character", "value"),
     Input("escape-character", "value"),
     Input("header-settings", "value"),
     Input("file-encoding", "value")],
    prevent_initial_call=True
)
def show_file_preview(file_path, delimiter, quote_char, escape_char, header, encoding):
    if not file_path:
        return [], [], "No file available for preview.", "", ""

    csv_settings = {
        "delimiter": delimiter or ",",
        "quote_char": quote_char or '"',
        "escape_char": escape_char or '"',
        "header": header if header is not None else True,
        "encoding": encoding or "utf-8"
    }

    filename = file_path.split("/")[-1]
    try:
        df = read_file_from_volume(
            DATABRICKS_VOLUME_PATH, 
            filename, 
            delimiter=csv_settings["delimiter"],
            quote_char=csv_settings["quote_char"],
            header=csv_settings["header"],
            encoding=csv_settings["encoding"],
            limit=10
        )

        if not df.empty:
            # Prepare columns with types
            columns = [
                {"name": col, "id": col, 
                 "type": str(df[col].dtype)} 
                for col in df.columns
            ]
            
            # Convert data to records
            data = df.to_dict("records")
            
            # Create metadata string
            preview_metadata = f"Previewing {len(data)} rows, {len(df.columns)} columns"
            
            # Create datatype information
            datatype_info = html.Table(
                [html.Tr([html.Th("Column"), html.Th("Type")])] +
                [html.Tr([html.Td(col), html.Td(str(df[col].dtype))]) 
                 for col in df.columns],
                className="table table-sm"
            )
            
            return data, columns, f"File retrieved: {filename}", preview_metadata, datatype_info
        else:
            return [], [], "File not found or error processing file.", "", ""
    except Exception as e:
        return [], [], f"Error processing file: {str(e)}", "", ""