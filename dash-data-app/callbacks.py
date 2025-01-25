from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html
from dbutils import list_catalogs, list_schemas, list_tables, describe_table, get_sample_data

def register_callbacks(app):
    # Toggle modal for table selection
    @app.callback(
        Output("table-selection-modal", "is_open"),
        [Input("upload-trigger", "n_clicks"), Input("close-modal", "n_clicks")],
        [State("table-selection-modal", "is_open")]
    )
    def toggle_modal(open_click, close_click, is_open):
        if open_click or close_click:
            return not is_open
        return is_open

    # Load catalog options when modal opens
    @app.callback(
        Output("catalog-dropdown", "options"),
        Input("table-selection-modal", "is_open"),
        prevent_initial_call=True
    )
    def load_catalogs(is_open):
        if is_open:
            df = list_catalogs()
            return [{'label': catalog, 'value': catalog} for catalog in df.iloc[:, 0].tolist()]
        return []

    # Load schemas when catalog is selected
    @app.callback(
        [Output("schema-dropdown", "options"),
         Output("schema-dropdown", "disabled")],
        Input("catalog-dropdown", "value")
    )
    def load_schemas(selected_catalog):
        if not selected_catalog:
            return [], True
        
        df = list_schemas(selected_catalog)
        return [{'label': schema, 'value': schema} for schema in df.iloc[:, 0].tolist()], False

    # Load tables when schema is selected
    @app.callback(
        [Output("table-dropdown", "options"),
         Output("table-dropdown", "disabled")],
        [Input("catalog-dropdown", "value"),
         Input("schema-dropdown", "value")]
    )
    def load_tables(selected_catalog, selected_schema):
        if not selected_catalog or not selected_schema:
            return [], True
        
        df = list_tables(selected_catalog, selected_schema)
        return [{'label': table, 'value': table} for table in df['tableName'].tolist()], False

    # Show selected table path
    @app.callback(
        Output("selected-table-path", "children"),
        [Input("catalog-dropdown", "value"),
         Input("schema-dropdown", "value"),
         Input("table-dropdown", "value")]
    )
    def update_selected_table(catalog, schema, table):
        if catalog and schema and table:
            return f"Selected Table: {catalog} > {schema} > {table}"
        return html.Span("Please select a catalog, schema, and table.", className="text-danger fw-bold")

    # Display table schema and sample data after selection
    @app.callback(
        [Output("table-schema", "children"),
         Output("sample-data", "children")],
        Input("table-dropdown", "value"),
        State("catalog-dropdown", "value"),
        State("schema-dropdown", "value")
    )
    def display_table_details(selected_table, selected_catalog, selected_schema):
        if not selected_catalog or not selected_schema or not selected_table:
            return html.P("No data available"), html.P("No data available")

        # Get the table schema and sample data
        schema_df = describe_table(selected_catalog, selected_schema, selected_table)
        sample_df = get_sample_data(selected_catalog, selected_schema, selected_table, limit=5)

        # Rename columns for better display
        schema_df.columns = ["Column Name", "Data Type", "Comment"]

        schema_table = dbc.Table.from_dataframe(
            schema_df,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            style={"max-width": "40%", "margin": "0 auto"}  # Adjust width to smaller and center
        )

        sample_table = dbc.Table.from_dataframe(
            sample_df,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            style={"width": "100%", "margin": "0 auto"}
        )

        return schema_table, sample_table