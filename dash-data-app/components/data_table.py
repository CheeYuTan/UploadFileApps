import dash.dash_table as dt

def get_data_table(table_id: str, **kwargs):
    """Returns a configured DataTable with consistent styling"""
    default_props = {
        "style_table": {"width": "100%"},
        "style_cell": {
            'textAlign': 'left',
            'padding': '8px',
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        "style_header": {
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        "style_data_conditional": [{
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }]
    }
    
    # Merge default props with any custom props
    table_props = {**default_props, **kwargs}
    return dt.DataTable(id=table_id, **table_props) 