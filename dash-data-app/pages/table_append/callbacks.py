from dash import callback, Input, Output, State
from typing import Dict, List, Tuple, Optional
from .utils import get_data_type_icon, infer_column_type, create_header_conditional
# ... (rest of imports)

@callback(
    [Output("table-preview", "data"),
     Output("table-preview", "columns"),
     Output("table-preview-metadata", "children"),
     Output("table-preview-section", "style"),
     Output("table-preview", "tooltip_header"),
     Output("table-preview", "style_header_conditional")],
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
) -> Tuple[List[dict], List[dict], str, dict, dict, List[dict]]:
    # ... (existing callback code using the utility functions) ... 