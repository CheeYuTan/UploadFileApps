import dash
import dash_bootstrap_components as dbc
import dash.dash_table as dt
from dash import html, dcc, callback, Input, Output, State
from dbutils import (
    read_file_from_volume, 
    list_catalogs, 
    list_schemas, 
    list_tables,
    describe_table,
    get_sample_data
)
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

    # File Preview Section
    html.H5("File Preview", className="fw-bold mt-4"),
    html.Div(id="file-preview-metadata", className="text-muted small mb-2"),
    dcc.Loading(
        id="loading-preview",
        type="circle",
        children=dt.DataTable(
            id="file-preview", 
            style_table={"width": "100%"}
        )
    ),

    dbc.Button("Advanced Attributes", id="advanced-attributes-btn", color="primary", className="mt-3"),
    get_csv_settings_modal(),

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
            # Add table preview section
            html.Div([
                html.H6("Target Table Preview", className="mt-4"),
                html.Div(id="table-preview-metadata", className="text-muted small mb-2"),
                dcc.Loading(
                    id="loading-table-preview",
                    type="circle",
                    children=dt.DataTable(id="table-preview", style_table={"width": "100%"})
                )
            ], id="table-preview-section", style={"display": "none"}),
        ])
    ]),

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
    [Output("table-preview", "data"),
     Output("table-preview", "columns"),
     Output("table-preview-metadata", "children"),
     Output("table-preview-section", "style")],
    [Input("catalog-select", "value"),
     Input("schema-select", "value"),
     Input("table-select", "value")]
)
def update_table_preview(catalog, schema, table):
    if not all([catalog, schema, table]):
        return [], [], "", {"display": "none"}
    
    try:
        # Get table schema and sample data
        schema_df = describe_table(catalog, schema, table)
        sample_df = get_sample_data(catalog, schema, table, limit=5)
        
        if not sample_df.empty:
            # Remove _rescued_data column if it exists
            if '_rescued_data' in sample_df.columns:
                sample_df = sample_df.drop('_rescued_data', axis=1)
            
            # Convert all values to string to ensure they're displayable
            sample_df = sample_df.astype(str)
            
            columns = [{"name": col, "id": col} for col in sample_df.columns]
            data = sample_df.to_dict("records")
            
            # Create schema table
            schema_table = dt.DataTable(
                id="schema-table",
                columns=[
                    {"name": "Column", "id": "column"},
                    {"name": "Type", "id": "type"}
                ],
                data=[
                    {"column": row['col_name'], "type": row['data_type']}
                    for _, row in schema_df.iterrows()
                    if row['col_name'] != '_rescued_data'
                ],
                style_table={"width": "100%"},
                style_cell={'textAlign': 'left'},
                style_header={'fontWeight': 'bold'}
            )
            
            # Create metadata with row/column count and schema table
            metadata = html.Div([
                html.Div(f"Showing 5 rows, {len(sample_df.columns)} columns", className="mb-2"),
                html.H6("Table Schema:", className="mt-3 mb-2"),
                schema_table
            ])
            
            return data, columns, metadata, {"display": "block"}
    except Exception as e:
        print(f"Error loading table preview: {str(e)}")
    
    return [], [], "", {"display": "none"}

@callback(
    [Output("file-preview", "data"),
     Output("file-preview", "columns"),
     Output("file-info", "children"),
     Output("file-preview-metadata", "children")],
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
        return [], [], "No file available for preview.", ""

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
            # Remove _rescued_data column if it exists
            if '_rescued_data' in df.columns:
                df = df.drop('_rescued_data', axis=1)
            
            columns = [{"name": col, "id": col} for col in df.columns]
            data = df.to_dict("records")
            preview_metadata = f"Showing {len(data)} rows, {len(df.columns)} columns"
            
            return data, columns, f"File retrieved: {filename}", preview_metadata
        else:
            return [], [], "File not found or error processing file.", ""
    except Exception as e:
        return [], [], f"Error processing file: {str(e)}", ""