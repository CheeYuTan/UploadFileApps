import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True
)

app.layout = dbc.Container([
    dash.page_container
])

if __name__ == "__main__":
    app.run(debug=True)