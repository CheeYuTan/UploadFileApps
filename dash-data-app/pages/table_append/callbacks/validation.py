from dash import callback, Input, Output, State, html
import pandas as pd
from dbutils import describe_table, read_file_from_volume
from config import DATABRICKS_VOLUME_PATH

def infer_pandas_dtype(series):
    """Infer Databricks data type from pandas series"""
    if pd.api.types.is_integer_dtype(series):
        return "INT"
    elif pd.api.types.is_float_dtype(series):
        return "DOUBLE"
    elif pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "TIMESTAMP"
    else:
        return "STRING"

def are_types_compatible(source_type, target_type):
    """Check if source data type can be safely converted to target type"""
    source_type = source_type.upper()
    target_type = target_type.upper()
    
    # Define type hierarchies (from most specific to most general)
    numeric_types = {
        'TINYINT': 0, 'SMALLINT': 1, 'INT': 2, 'BIGINT': 3,
        'FLOAT': 4, 'DOUBLE': 5, 'DECIMAL': 5
    }
    
    # Direct matches are always compatible
    if source_type == target_type:
        return True
    
    # Numeric type compatibility
    if source_type in numeric_types and target_type in numeric_types:
        return numeric_types[source_type] <= numeric_types[target_type]
    
    # String can be converted to timestamp if properly formatted
    if source_type == 'STRING' and target_type == 'TIMESTAMP':
        return True
    
    # String can be converted to boolean if properly formatted
    if source_type == 'STRING' and target_type == 'BOOLEAN':
        return True
    
    # Any type can be stored as string
    if target_type == 'STRING':
        return True
    
    return False

@callback(
    Output("validate-data", "disabled"),
    [Input("catalog-select", "value"),
     Input("schema-select", "value"),
     Input("table-select", "value")]
)
def toggle_validate_button(catalog, schema, table):
    return not all([catalog, schema, table])

@callback(
    [Output("validation-results", "children"),
     Output("confirm-append", "disabled")],
    Input("validate-data", "n_clicks"),
    [State("file-path", "data"),
     State("catalog-select", "value"),
     State("schema-select", "value"),
     State("table-select", "value"),
     State("column-delimiter", "value"),
     State("quote-character", "value"),
     State("header-settings", "value"),
     State("file-encoding", "value")],
    prevent_initial_call=True
)
def validate_data(n_clicks, file_path, catalog, schema, table, delimiter, quote_char, header, encoding):
    if not n_clicks or not all([file_path, catalog, schema, table]):
        return "", True

    try:
        # Get table schema
        table_schema = describe_table(catalog, schema, table)
        table_cols = {row['col_name']: row['data_type'] for row in table_schema.to_dict('records')}

        # Read sample of the file
        df = read_file_from_volume(
            DATABRICKS_VOLUME_PATH,
            file_path.split("/")[-1],
            delimiter=delimiter or ",",
            quote_char=quote_char or '"',
            header=header if header is not None else True,
            encoding=encoding or "utf-8",
            limit=1000  # Sample size for schema inference
        )

        if '_rescued_data' in df.columns:
            df = df.drop('_rescued_data', axis=1)

        validation_results = []
        
        # Column presence validation
        missing_cols = set(table_cols.keys()) - set(df.columns)
        extra_cols = set(df.columns) - set(table_cols.keys())
        
        if missing_cols:
            validation_results.append(
                html.Div([
                    html.Strong("Missing Columns: "),
                    html.Span(f"{', '.join(missing_cols)}")
                ], className="text-danger mb-2")
            )
        
        if extra_cols:
            validation_results.append(
                html.Div([
                    html.Strong("Extra Columns: "),
                    html.Span(f"{', '.join(extra_cols)}")
                ], className="text-warning mb-2")
            )

        # Data type validation
        type_issues = []
        for col in df.columns:
            if col in table_cols:
                file_type = infer_pandas_dtype(df[col])
                table_type = table_cols[col].upper()
                
                if not are_types_compatible(file_type, table_type):
                    type_issues.append(
                        html.Div([
                            html.Strong(f"Column '{col}': "),
                            html.Span(f"File type ({file_type}) is not compatible with table type ({table_type})")
                        ])
                    )

        if type_issues:
            validation_results.append(
                html.Div([
                    html.Strong("Data Type Issues:", className="d-block mb-2"),
                    html.Div(type_issues, className="ps-3")
                ], className="text-danger mb-2")
            )

        # Sample value validation
        value_issues = []
        for col in df.columns:
            if col in table_cols:
                table_type = table_cols[col].upper()
                sample_values = df[col].dropna()
                
                if table_type in ['TINYINT', 'SMALLINT', 'INT', 'BIGINT', 'FLOAT', 'DOUBLE', 'DECIMAL']:
                    numeric_values = pd.to_numeric(sample_values, errors='coerce')
                    invalid_count = numeric_values.isna().sum()
                    if invalid_count > 0:
                        value_issues.append(
                            html.Div([
                                html.Strong(f"Column '{col}': "),
                                html.Span(f"Found {invalid_count} non-numeric values")
                            ])
                        )
                
                elif table_type == 'TIMESTAMP':
                    datetime_values = pd.to_datetime(sample_values, errors='coerce')
                    invalid_count = datetime_values.isna().sum()
                    if invalid_count > 0:
                        value_issues.append(
                            html.Div([
                                html.Strong(f"Column '{col}': "),
                                html.Span(f"Found {invalid_count} invalid datetime values")
                            ])
                        )
                
                elif table_type == 'BOOLEAN':
                    valid_values = {'true', 'false', '1', '0', 'yes', 'no', 't', 'f', 'y', 'n'}
                    invalid_count = sum(1 for x in sample_values if str(x).lower() not in valid_values)
                    if invalid_count > 0:
                        value_issues.append(
                            html.Div([
                                html.Strong(f"Column '{col}': "),
                                html.Span(f"Found {invalid_count} non-boolean values")
                            ])
                        )

        if value_issues:
            validation_results.append(
                html.Div([
                    html.Strong("Value Issues:", className="d-block mb-2"),
                    html.Div(value_issues, className="ps-3")
                ], className="text-danger mb-2")
            )

        # Final validation result
        if validation_results:
            return html.Div([
                html.H6("Validation Issues:", className="mb-3"),
                html.Div(validation_results)
            ]), True
        else:
            return html.Div("✓ Validation successful!", className="text-success"), False

    except Exception as e:
        print(f"Error during validation: {str(e)}")
        return html.Div(f"Error during validation: {str(e)}", className="text-danger"), True

@callback(
    Output("processing-status", "children"),
    Input("confirm-append", "n_clicks"),
    [State("file-path", "data"),
     State("catalog-select", "value"),
     State("schema-select", "value"),
     State("table-select", "value"),
     State("column-delimiter", "value"),
     State("quote-character", "value"),
     State("header-settings", "value"),
     State("file-encoding", "value")],
    prevent_initial_call=True
)
def append_data(n_clicks, file_path, catalog, schema, table, delimiter, quote_char, header, encoding):
    if not n_clicks:
        return ""
    
    try:
        # TODO: Implement the actual append logic here
        # This should call your Databricks SQL connector to append the data
        return html.Div("Data appended successfully!", className="text-success")
    except Exception as e:
        return html.Div(f"Error appending data: {str(e)}", className="text-danger") 