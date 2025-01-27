import dash
import dash_bootstrap_components as dbc
import dash.dash_table as dt
from dash import html, dcc, callback, Input, Output, State, ctx
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
import os
from typing import Dict, List, Tuple, Optional
import pandas as pd
from dash_bootstrap_components import Tooltip

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
                'fontWeight': 'bold',
                'cursor': 'help'  # Show cursor on header hover
            },
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }],
            tooltip_data=[],  # Will be populated by callback
            tooltip_duration=None,  # Show tooltip until hover off
            css=[{
                'selector': '.dash-table-tooltip',
                'rule': 'background-color: white; font-size: 12px; padding: 5px;'
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
                            'fontWeight': 'bold',
                            'cursor': 'help'
                        },
                        style_data_conditional=[{
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }],
                        tooltip_data=[],
                        tooltip_duration=None,
                        css=[{
                            'selector': '.dash-table-tooltip',
                            'rule': 'background-color: white; font-size: 12px; padding: 5px;'
                        }]
                    )
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

def get_data_type_icon(data_type: str) -> html.Img:
    """Returns the appropriate icon for a given data type"""
    data_type = data_type.upper()
    
    icon_path = "assets/data-types/"
    
    if data_type in ['TINYINT', 'SMALLINT', 'INT', 'BIGINT']:
        return html.Img(src=icon_path + "Integral_Numeric.png", height="20px", style={"marginRight": "5px"})
    elif data_type in ['BINARY']:
        return html.Img(src=icon_path + "Binary.png", height="20px", style={"marginRight": "5px"})
    elif data_type in ['BOOLEAN']:
        return html.Img(src=icon_path + "Boolean.png", height="20px", style={"marginRight": "5px"})
    elif data_type in ['ARRAY', 'MAP', 'STRUCT', 'VARIANT', 'OBJECT']:
        return html.Img(src=icon_path + "Complex.png", height="20px", style={"marginRight": "5px"})
    elif data_type in ['DATE']:
        return html.Img(src=icon_path + "Date.png", height="20px", style={"marginRight": "5px"})
    elif data_type in ['TIMESTAMP', 'TIMESTAMP_NTZ']:
        return html.Img(src=icon_path + "Datetime.png", height="20px", style={"marginRight": "5px"})
    elif data_type in ['DECIMAL']:
        return html.Img(src=icon_path + "Decimal.png", height="20px", style={"marginRight": "5px"})
    elif data_type in ['FLOAT', 'DOUBLE']:
        return html.Img(src=icon_path + "Float.png", height="20px", style={"marginRight": "5px"})
    elif data_type in ['STRING']:
        return html.Img(src=icon_path + "String.png", height="20px", style={"marginRight": "5px"})
    else:
        return None

def get_table_schema(catalog: str, schema: str, table: str) -> Dict[str, str]:
    """Get the schema of a table with column names and data types.
    
    Args:
        catalog: The catalog name
        schema: The schema name 
        table: The table name
        
    Returns:
        Dict mapping column names to their data types
    """
    try:
        df = describe_table(catalog, schema, table)
        return dict(zip(df['col_name'], df['data_type']))
    except Exception as e:
        print(f"Error getting table schema: {str(e)}")
        return {}

def generate_metadata_text(df: pd.DataFrame) -> str:
    """Generate metadata text describing the dataframe.
    
    Args:
        df: The pandas DataFrame
        
    Returns:
        String with metadata description
    """
    return f"Table contains {len(df)} rows and {len(df.columns)} columns"

@callback(
    [Output("table-preview", "data"),
     Output("table-preview", "columns"),
     Output("table-preview-metadata", "children"),
     Output("table-preview-section", "style")],
    [Input("catalog-select", "value"),
     Input("schema-select", "value"),
     Input("table-select", "value")],
    background=True,
    running=[
        (Output("table-preview", "style"), {"opacity": "0.5"}, {"opacity": "1"}),
        (Output("confirm-append", "disabled"), True, False)
    ]
)
def update_table_preview(
    catalog: Optional[str], 
    schema: Optional[str], 
    table: Optional[str]
) -> Tuple[List[dict], List[dict], str, dict]:
    if not all([catalog, schema, table]):
        return [], [], "", {"display": "none"}
    
    try:
        # Get sample data and schema
        sample_df = get_sample_data(catalog, schema, table, limit=10)
        schema_df = describe_table(catalog, schema, table)
        data_types = dict(zip(schema_df['col_name'], schema_df['data_type']))
        
        # Create columns with tooltips
        columns = []
        for col in sample_df.columns:
            data_type = data_types.get(col, "").upper()
            columns.append({
                "name": f"ⓘ {col}",  # Add an info icon character
                "id": col,
                "type": "numeric" if data_type in ["INT", "FLOAT", "DECIMAL"] else "text",
                "tooltip": f"Type: {data_type}"  # Add tooltip directly to column
            })
        
        return (
            sample_df.to_dict('records'),
            columns,
            f"Showing {len(sample_df)} sample rows",
            {"display": "block"}
        )
        
    except Exception as e:
        print(f"Error updating table preview: {str(e)}")
        return [], [], f"Error: {str(e)}", {"display": "none"}

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
            if '_rescued_data' in df.columns:
                df = df.drop('_rescued_data', axis=1)
            
            # Create columns with inferred types
            columns = []
            for col in df.columns:
                # Infer data type
                sample_values = df[col].dropna()
                if len(sample_values) > 0:
                    if pd.api.types.is_numeric_dtype(sample_values):
                        data_type = "FLOAT" if all(sample_values.astype(str).str.contains('\.').fillna(False)) else "INT"
                        col_type = "numeric"
                    elif pd.api.types.is_datetime64_any_dtype(sample_values):
                        data_type = "TIMESTAMP"
                        col_type = "text"
                    elif pd.api.types.is_bool_dtype(sample_values):
                        data_type = "BOOLEAN"
                        col_type = "text"
                    else:
                        data_type = "STRING"
                        col_type = "text"
                else:
                    data_type = "STRING"
                    col_type = "text"
                
                columns.append({
                    "name": f"ⓘ {col}",
                    "id": col,
                    "type": col_type,
                    "tooltip": f"Type: {data_type}"  # Add tooltip directly to column
                })
            
            preview_metadata = f"Showing {len(df)} rows, {len(df.columns)} columns"
            return df.to_dict("records"), columns, f"File retrieved: {filename}", preview_metadata
        else:
            return [], [], "File not found or error processing file.", ""
    except Exception as e:
        return [], [], f"Error processing file: {str(e)}", ""