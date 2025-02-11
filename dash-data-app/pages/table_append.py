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
    get_sample_data,
    insert_data_to_table
)
from config import DATABRICKS_VOLUME_PATH
from components.csv_settings import get_csv_settings_modal
import os
import pandas as pd

os.makedirs("./cache", exist_ok=True)

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
            style_table={"width": "100%"},
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }]
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
                html.H6("Table Preview", className="mt-4"),
                html.Div(id="table-preview-metadata", className="text-muted mb-2"),
                dcc.Loading(
                    id="loading-table-preview",
                    type="circle",
                    children=dt.DataTable(
                        id="table-preview",
                        style_table={"width": "100%"},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '8px',
                            'whiteSpace': 'normal',
                            'height': 'auto',
                        },
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        },
                        style_data_conditional=[{
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }]
                    )
                )
            ], id="table-preview-section", style={"display": "none"}),
        ])
    ]),

    # Add validation and append buttons
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

    # Add validation results section
    html.Div(id="validation-results", className="mt-3"),

    dcc.Store(id="file-path", storage_type="session"),
    dcc.Store(id="csv-settings", storage_type="session"),
    dcc.Store(id="validation-state", data=False),

    # Update the layout to include a modal for success message
    dbc.Modal([
        dbc.ModalHeader("Success"),
        dbc.ModalBody([
            html.I(className="fas fa-check-circle me-2 text-success"),
            html.Span(id="success-message"),
            html.Hr(),
            html.P("Would you like to upload another file?", className="mb-0")
        ]),
        dbc.ModalFooter([
            dbc.Button("Upload Another", href="/", color="primary"),
            dbc.Button("Close", id="close-success-modal", className="ms-2")
        ])
    ], id="success-modal", is_open=False),

    # Add loading overlay for append operation
    dbc.Spinner(
        html.Div(
            id="append-overlay",
            style={
                "position": "fixed",
                "top": 0,
                "left": 0,
                "right": 0,
                "bottom": 0,
                "backgroundColor": "rgba(0, 0, 0, 0.5)",
                "zIndex": 1000,
                "display": "none"
            }
        ),
        color="primary",
        fullscreen=True,
    )
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
    Input("file-path", "data")
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
     Output("table-preview-section", "style"),
     Output("confirm-append", "disabled")],
    [Input("catalog-select", "value"),
     Input("schema-select", "value"),
     Input("table-select", "value"),
     Input("validation-state", "data")],
    background=True,
    running=[
        (Output("table-preview", "style"), {"opacity": "0.5"}, {"opacity": "1"}),
    ]
)
def update_table_preview(catalog, schema, table, is_validated):
    if not all([catalog, schema, table]):
        return [], [], "", {"display": "none"}, True
    
    try:
        # Get sample data
        sample_df = get_sample_data(catalog, schema, table, limit=10)
        
        # Create simple columns
        columns = [{"name": col, "id": col} for col in sample_df.columns]
        
        return (
            sample_df.to_dict('records'),
            columns,
            f"Showing {len(sample_df)} sample rows, {len(sample_df.columns)} columns",
            {"display": "block"},
            not is_validated  # Disable append button unless validation passed
        )
        
    except Exception as e:
        print(f"Error updating table preview: {str(e)}")
        return [], [], f"Error: {str(e)}", {"display": "none"}, True

@callback(
    [Output("file-preview", "data"),
     Output("file-preview", "columns"),
     Output("file-info", "children"),
     Output("file-preview-metadata", "children")],
    [Input("file-path", "data"),
     Input("column-delimiter", "value"),
     Input("quote-character", "value"),
     Input("header-settings", "value"),
     Input("file-encoding", "value")],
    prevent_initial_call=True
)
def show_file_preview(file_path, delimiter, quote_char, header, encoding):
    if not file_path:
        return [], [], "No file available for preview.", ""

    csv_settings = {
        "delimiter": delimiter or ",",
        "quote_char": quote_char or '"',
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
            if '_rescued_data' in df.columns:
                df = df.drop('_rescued_data', axis=1)
            
            # Create simple columns
            columns = [{"name": col, "id": col} for col in df.columns]
            
            preview_metadata = f"Showing {len(df)} rows, {len(df.columns)} columns"
            return (
                df.to_dict("records"),
                columns,
                f"File retrieved: {filename}",
                preview_metadata
            )
        else:
            return [], [], "File not found or error processing file.", ""
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return [], [], f"Error processing file: {str(e)}", ""

@callback(
    [Output("validation-results", "children"),
     Output("confirm-append", "disabled", allow_duplicate=True),
     Output("validation-state", "data")],
    Input("validate-data", "n_clicks"),
    [State("file-path", "data"),
     State("catalog-select", "value"),
     State("schema-select", "value"),
     State("table-select", "value"),
     State("column-delimiter", "value"),
     State("quote-character", "value"),
     State("header-settings", "value"),
     State("file-encoding", "value")],
    prevent_initial_call=True,
    running=[
        (Output("validate-data", "disabled"), True, False),
        (Output("validate-data", "children"), "Validating...", "Validate Data")
    ]
)
def validate_data(n_clicks, file_path, catalog, schema, table, delimiter, quote_char, header, encoding):
    if not n_clicks or not all([file_path, catalog, schema, table]):
        return "", True, False

    try:
        validation_results = []
        
        # Get table schema
        schema_df = describe_table(catalog, schema, table)
        table_dtypes = dict(zip(schema_df['col_name'], schema_df['data_type']))

        # Add validation header
        validation_results.append(
            html.H6("Validation Results:", className="mt-3 mb-3")
        )

        # File check
        if not file_path.lower().endswith('.csv'):
            validation_results.append(
                html.Div("❌ Invalid file type. Only CSV files are supported.", 
                        className="text-danger mb-2")
            )
            return html.Div(validation_results), True, False

        # Read the file
        csv_settings = {
            "delimiter": delimiter or ",",
            "quote_char": quote_char or '"',
            "header": header if header is not None else True,
            "encoding": encoding or "utf-8"
        }

        df = read_file_from_volume(
            DATABRICKS_VOLUME_PATH,
            file_path.split("/")[-1],
            **csv_settings
        )

        if '_rescued_data' in df.columns:
            df = df.drop('_rescued_data', axis=1)

        # Validate columns
        missing_cols = set(table_dtypes.keys()) - set(df.columns)
        extra_cols = set(df.columns) - set(table_dtypes.keys())
        validation_errors = []

        if missing_cols:
            validation_errors.append(
                html.Div(f"Missing columns in file: {', '.join(missing_cols)}", 
                        className="text-danger")
            )
        
        if extra_cols:
            validation_errors.append(
                html.Div(f"Extra columns in file: {', '.join(extra_cols)}", 
                        className="text-danger")
            )

        # Validate data types
        type_errors = []
        for col in df.columns:
            if col in table_dtypes:
                expected_type = table_dtypes[col].upper()
                # Add data type validation logic here
                sample_values = df[col].dropna()
                
                if expected_type in ['TINYINT', 'SMALLINT', 'INT', 'BIGINT']:
                    if not pd.to_numeric(sample_values, errors='coerce').notna().all():
                        type_errors.append(f"Column '{col}' should be INTEGER type")
                
                elif expected_type in ['FLOAT', 'DOUBLE', 'DECIMAL']:
                    if not pd.to_numeric(sample_values, errors='coerce').notna().all():
                        type_errors.append(f"Column '{col}' should be NUMERIC type")
                
                elif expected_type == 'TIMESTAMP':
                    if not pd.to_datetime(sample_values, errors='coerce').notna().all():
                        type_errors.append(f"Column '{col}' should be TIMESTAMP type")
                
                elif expected_type == 'BOOLEAN':
                    valid_values = {'true', 'false', '1', '0', 'yes', 'no'}
                    if not sample_values.astype(str).str.lower().isin(valid_values).all():
                        type_errors.append(f"Column '{col}' should be BOOLEAN type")

        if type_errors:
            validation_errors.extend([
                html.Div(error, className="text-danger")
                for error in type_errors
            ])

        if validation_errors:
            validation_results.extend([
                html.Div([
                    html.I(className="fas fa-times-circle me-2"),
                    error
                ], className="text-danger mb-2")
                for error in validation_errors
            ])
            return html.Div(validation_results), True, False
        else:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-check-circle me-2"),
                    "Validation successful!"
                ], className="text-success")
            ]), False, True

    except Exception as e:
        return html.Div([
            html.Div([
                html.I(className="fas fa-exclamation-circle me-2"),
                f"Error during validation: {str(e)}"
            ], className="text-danger")
        ]), True, False

@callback(
    [Output("processing-status", "children"),
     Output("append-overlay", "style"),
     Output("success-modal", "is_open"),
     Output("success-message", "children")],
    Input("confirm-append", "n_clicks"),
    [State("file-path", "data"),
     State("catalog-select", "value"),
     State("schema-select", "value"),
     State("table-select", "value"),
     State("column-delimiter", "value"),
     State("quote-character", "value"),
     State("header-settings", "value"),
     State("file-encoding", "value"),
     State("validation-state", "data")],
    prevent_initial_call=True,
    running=[
        (Output("confirm-append", "disabled", allow_duplicate=True), True, False),
        (Output("confirm-append", "children"),
         html.Div([
             dbc.Spinner(size="sm", color="light"),
             html.Span("Inserting data...", className="ms-2")
         ]),
         "Confirm and Append Data")
    ]
)
def append_data(n_clicks, file_path, catalog, schema, table, delimiter, quote_char, header, encoding, is_validated):
    if not n_clicks or not is_validated:
        return "", {"display": "none"}, False, ""
    
    overlay_style = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "right": 0,
        "bottom": 0,
        "backgroundColor": "rgba(0, 0, 0, 0.5)",
        "zIndex": 1000,
        "display": "block"
    }
    
    try:
        # Read the file with settings
        csv_settings = {
            "delimiter": delimiter or ",",
            "quote_char": quote_char or '"',
            "header": header if header is not None else True,
            "encoding": encoding or "utf-8"
        }
        
        # Read the file to get total rows
        df = read_file_from_volume(
            DATABRICKS_VOLUME_PATH,
            file_path.split("/")[-1],
            **csv_settings,
            limit=None  # Read all rows
        )
        
        if '_rescued_data' in df.columns:
            df = df.drop('_rescued_data', axis=1)
        
        # Get the total number of rows
        total_rows = len(df)
        
        # Insert the data and get rows inserted
        rows_inserted = insert_data_to_table(
            catalog=catalog,
            schema=schema,
            table=table,
            data=df,
            file_path=file_path,
            header=csv_settings["header"],
            delimiter=csv_settings["delimiter"],
            quote_char=csv_settings["quote_char"],
            encoding=csv_settings["encoding"]
        )
        
        success_message = (
            f"Successfully inserted {rows_inserted:,} rows into {catalog}.{schema}.{table}. "
            f"Click 'Upload Another' to process another file or 'Close' to stay on this page."
        )
        return "", {"display": "none"}, True, success_message
        
    except Exception as e:
        print(f"Error appending data: {str(e)}")
        return html.Div([
            html.Div([
                html.I(className="fas fa-exclamation-circle me-2"),
                "Error appending data:"
            ], className="text-danger fw-bold"),
            html.Div(str(e), className="text-danger ms-4 mt-2")
        ]), {"display": "none"}, False, ""

@callback(
    Output("validate-data", "disabled"),
    [Input("catalog-select", "value"),
     Input("schema-select", "value"),
     Input("table-select", "value"),
     Input("table-preview", "data")]
)
def toggle_validate_button(catalog, schema, table, preview_data):
    return not (all([catalog, schema, table]) and preview_data)

@callback(
    Output("success-modal", "is_open", allow_duplicate=True),
    Input("close-success-modal", "n_clicks"),
    prevent_initial_call=True
)
def close_success_modal(n_clicks):
    return False