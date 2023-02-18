import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

biljke = ["PITOMI_KESTEN", "KOPRIVE", "BOR", "TRAVE", "LIPA", "TRPUTAC", "MASLINA", "HRAST_CRNIKA", "CRKVINA",
          "CEMPRESI", "AMBROZIJA", "HRAST", "LOBODA", "HRAST_SP", "PELIN"]

# TODO https://dash.plotly.com/interactive-graphing
# TODO Filtrirati po: 1. biljka, 2. grad, 3. godina, 4. mjesec (try-except ako file ne postoji)

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children=f'Razina peludi:', style={
        'textAlign': 'center'
    }),
    html.Div(
        dcc.Dropdown(['Zagreb', 'Split', 'Pula', 'Dubrovnik', 'Zadar'], 'Zagreb', id='city-dropdown'),
        style={'width': '25%', 'display': 'inline-block'}),
    html.Div(
        dcc.Dropdown(biljke, "AMBROZIJA", id='plant-dropdown'), style={'width': '25%', 'display': 'inline-block'}),
    html.Div(
        dcc.Dropdown(list(range(1, 13)), 9, id='month-dropdown'), style={'width': '25%', 'display': 'inline-block'}),
    html.Div(
        dcc.Dropdown([2022, 2023], 2022, id='year-dropdown'), style={'width': '25%', 'display': 'inline-block'}),
    dcc.Graph(id="graph"),
    html.P(
        children='Izvor podataka: Nastavni zavod za javno zdravstvo \"Dr. Andrija Štampar\", https://stampar.hr/hr/peludna-prognoza',
        style={
            'textAlign': 'center'
        })
])


@app.callback(Output("graph", "figure"), Input('city-dropdown', 'value'), Input('plant-dropdown', 'value'),
              Input('month-dropdown', 'value'), Input('year-dropdown', 'value'))
def display_graph(i_grad, i_biljka, i_mjesec, i_godina):
    file_path = f'./data/{i_godina}/{i_mjesec}/{i_grad} - {i_biljka} pelud za {i_mjesec}.{i_godina}'

    df = pd.read_csv(file_path, header=None, sep='  ', engine='python')

    fig = px.bar(df, x=1, y=0, labels={
        "1": "Datum",
        "0": "Razina peludi"
    })

    return fig


app.run_server(debug=True)
