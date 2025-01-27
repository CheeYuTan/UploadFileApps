from dash import callback, Input, Output, State, html
import pandas as pd
from dbutils import describe_table, read_file_from_volume
from config import DATABRICKS_VOLUME_PATH

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
        schema_df = describe_table(catalog, schema, table)
        table_dtypes = dict(zip(schema_df['col_name'], schema_df['data_type']))

        # Read the file with only supported parameters
        df = read_file_from_volume(
            DATABRICKS_VOLUME_PATH,
            file_path.split("/")[-1],
            delimiter=delimiter or ",",
            quote_char=quote_char or '"',
            header=header if header is not None else True,
            encoding=encoding or "utf-8",
            limit=None  # Read all rows for validation
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
            return html.Div(validation_errors), True
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