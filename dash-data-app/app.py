from dash import Dash, html
from dash.long_callback import DiskcacheLongCallbackManager
import diskcache
import dash_bootstrap_components as dbc

# Initialize the cache in a directory called 'cache'
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

# Pass the long_callback_manager to the Dash app
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    long_callback_manager=long_callback_manager
)

app.layout = dbc.Container([
    dash.page_container
])

if __name__ == "__main__":
    app.run(debug=True)