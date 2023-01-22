import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Razina peludi u Zagrebu'),
    html.Button("Switch Axis", n_clicks=0,
                id='button'),
    dcc.Graph(id="graph"),
])


@app.callback(Output("graph", "figure"), Input("button", "n_clicks"))
def display_graph(n_clicks):
    file_path = './data/2022/9/Zagreb - AMBROZIJA pelud za 9.2022'

    df = pd.read_csv(file_path, header=None, sep='  ', engine='python')

    fig = px.line(df, x=1, y=0)

    return fig


app.run_server(debug=True)
