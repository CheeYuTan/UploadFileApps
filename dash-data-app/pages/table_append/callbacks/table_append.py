from dash import callback, Input, Output, State, html
import dash_bootstrap_components as dbc
from dbutils import insert_data_to_table

@callback(
    [Output("append-status", "children"),
     Output("append-status", "is_open"),
     Output("confirm-append", "disabled"),
     Output("loading-append", "children")],
    Input("confirm-append", "n_clicks"),
    [State("catalog-select", "value"),
     State("schema-select", "value"),
     State("table-select", "value"),
     State("file-path", "data")],
    prevent_initial_call=True
)
def append_data_to_table(n_clicks, catalog, schema, table, file_path):
    if not n_clicks or not all([catalog, schema, table, file_path]):
        return "", False, False, ""
    
    try:
        # Show loading state
        rows_inserted = insert_data_to_table(
            catalog=catalog,
            schema=schema,
            table=table,
            file_path=file_path
        )
        
        success_alert = dbc.Alert(
            [
                html.I(className="bi bi-check-circle-fill me-2"),
                f"Successfully inserted {rows_inserted} rows into {catalog}.{schema}.{table}"
            ],
            color="success",
            dismissable=True,
            className="mt-3"
        )
        
        return success_alert, True, False, ""
        
    except Exception as e:
        error_alert = dbc.Alert(
            [
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                f"Error appending data: {str(e)}"
            ],
            color="danger",
            dismissable=True,
            className="mt-3"
        )
        
        return error_alert, True, False, "" 