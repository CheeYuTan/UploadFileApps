import dash
from .layout import get_layout
from . import callbacks  # This will register all callbacks

dash.register_page(__name__, path="/append-table")

layout = get_layout() 