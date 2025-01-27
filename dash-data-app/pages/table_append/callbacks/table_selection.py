from dash import callback, Input, Output
from dbutils import list_catalogs, list_schemas, list_tables, get_sample_data
import pandas as pd

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
def update_table_preview(catalog, schema, table):
    if not all([catalog, schema, table]):
        return [], [], "", {"display": "none"}
    
    try:
        # Get sample data
        sample_df = get_sample_data(catalog, schema, table, limit=10)
        
        print("Column types before conversion:")
        print(sample_df.dtypes)
        
        # Convert ALL columns to string first
        for col in sample_df.columns:
            try:
                sample_df[col] = sample_df[col].astype(str)
            except Exception as e:
                print(f"Error converting column {col}: {str(e)}")
                # If conversion fails, try converting individual values
                sample_df[col] = sample_df[col].apply(lambda x: str(x) if x is not None else '')
        
        print("Column types after conversion:")
        print(sample_df.dtypes)
        
        # Create simple columns
        columns = [{"name": col, "id": col} for col in sample_df.columns]
        
        # Convert to records with string values only
        records = sample_df.to_dict('records')
        
        # Debug first record
        print("First record before final conversion:")
        print(records[0] if records else "No records")
        
        # Ensure all values are strings
        for record in records:
            for key in record:
                try:
                    record[key] = str(record[key])
                except Exception as e:
                    print(f"Error converting value for {key}: {str(e)}")
                    record[key] = ''
        
        print("First record after final conversion:")
        print(records[0] if records else "No records")
        
        return (
            records,
            columns,
            f"Showing {len(sample_df)} sample rows, {len(sample_df.columns)} columns",
            {"display": "block"}
        )
        
    except Exception as e:
        print(f"Error updating table preview: {str(e)}")
        return [], [], f"Error: {str(e)}", {"display": "none"}

# ... (other table selection callbacks) ... 