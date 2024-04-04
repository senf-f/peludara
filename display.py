import os

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

biljke = ["PITOMI_KESTEN", "KOPRIVE", "BOR", "TRAVE", "LIPA", "TRPUTAC", "MASLINA", "HRAST_CRNIKA", "CRKVINA",
          "CEMPRESI", "AMBROZIJA", "HRAST", "LOBODA", "HRAST_SP", "PELIN"]


# TODO https://dash.plotly.com/interactive-graphing
# TODO Filtrirati po: 1. biljka, 2. grad, 3. godina, 4. mjesec (try-except ako file ne postoji)

# Function to read data directory structure
def read_data_directory(data_dir):
    cities = []
    years = []
    months = []

    for year_folder in os.listdir(data_dir):
        if os.path.isdir(os.path.join(data_dir, year_folder)):
            years.append(int(year_folder))
            for month_folder in os.listdir(os.path.join(data_dir, year_folder)):
                month = int(month_folder)
                if os.path.isdir(os.path.join(data_dir, year_folder, month_folder)):
                    months.append(month)
                    for file_name in os.listdir(os.path.join(data_dir, year_folder, month_folder)):
                        parts = file_name.split(' pelud za ')[0].split(' - ')
                        if len(parts) == 2:
                            city, plant = parts
                            if city not in cities:
                                cities.append(city)

    return cities, sorted(years), sorted(months)


# Function to get files for selected parameters
def get_file_path(data_dir, city, plant, year, month):
    file_name = f"{city} - {plant} pelud za {month}.{year}."
    file_path = os.path.join(data_dir, str(year), str(month), file_name)
    return file_path


# Define data directory
data_directory = "..\\ambrozija\data"

# Read data directory structure
cities, years, months = read_data_directory(data_directory)

app = Dash(__name__)

app.layout = html.Div([
    html.H2(children=f'Razina peludi:', style={
        'textAlign': 'center'
    }),
    html.Div(
        dcc.Dropdown(options=[{'label': city, 'value': city} for city in cities], value=cities[0], id='city-dropdown'),
        style={'width': '25%', 'display': 'inline-block'}),
    html.Div(dcc.Dropdown(options=[{'label': str(year), 'value': year} for year in years], value=years[0],
                          id='year-dropdown'),
             style={'width': '25%', 'display': 'inline-block'}),
    html.Div(dcc.Dropdown(options=[{'label': str(month), 'value': month} for month in months], value=months[0],
                          id='month-dropdown'),
             style={'width': '25%', 'display': 'inline-block'}),
    html.Div(
        dcc.Dropdown(biljke, "AMBROZIJA", id='plant-dropdown'), style={'width': '25%', 'display': 'inline-block'}),
    dcc.Graph(id="graph"),
    html.Div(id='warning-message', style={'textAlign': 'center', 'color': 'red'}),
    html.P(
        children='Izvor podataka: Nastavni zavod za javno zdravstvo \"Dr. Andrija Štampar\", https://stampar.hr/hr/peludna-prognoza',
        style={
            'textAlign': 'center'
        }),
    html.P(children="DEBUG P " + str(os.listdir(data_directory)) + "\n" + str(cities) + str(months) + str(years))
])


@app.callback([Output("graph", "figure"), Output("warning-message", "children")],
              [Input('city-dropdown', 'value'), Input('year-dropdown', 'value'), Input('month-dropdown', 'value'),
               Input('plant-dropdown', 'value')])
def display_graph_and_warning(city, year, month, plant):
    file_path = get_file_path(data_directory, city, plant, year, month)
    try:
        df = pd.read_csv(file_path, header=None, sep='  ', engine='python')
        if len(df.columns) >= 2:
            fig = px.bar(df, x=df.columns[1], y=df.columns[0], labels={"1": "Datum", "0": "Razina peludi"})
            return fig, None  # Return figure and no warning message if data is available
        else:
            return None, "Nema dostupnih podataka za odabrane parametre."  # Return no figure and warning message if data structure is unexpected
    except FileNotFoundError:
        return None, "Nema dostupnih podataka za odabrane parametre."


# @app.callback(Output("graph", "figure"), Input('city-dropdown', 'value'), Input('plant-dropdown', 'value'),
#               Input('month-dropdown', 'value'), Input('year-dropdown', 'value'))
# def display_graph(i_grad, i_biljka, i_mjesec, i_godina):
#     # poruka = f"Ne postoje podaci za biljku '{i_biljka}', za {i_mjesec}. mjesec {i_godina}. godine za {i_grad}"
#     # file_path = f'./data/{i_godina}/{i_mjesec}/{i_grad} - {i_biljka} pelud za {i_mjesec}.{i_godina}'
#     # df = pd.read_csv(file_path, header=None, sep='  ', engine='python')
#     #
#     # fig = px.bar(df, x=1, y=0, labels={
#     #     "1": "Datum",
#     #     "0": "Razina peludi"
#     # })
#
#     file_path = get_file_path(data_directory, i_grad, i_biljka, i_godina, i_mjesec)
#     try:
#         print(file_path)
#         df = pd.read_csv(file_path, header=None, sep='  ', engine='python')
#         if len(df.columns) >= 2:
#             fig = px.bar(df, x=df.columns[1], y=df.columns[0], labels={"1": "Datum", "0": "Razina peludi"})
#             return fig
#         else:
#             return px.bar(
#                 labels={"1": "Datum", "0": "Razina peludi"})  # Return an empty graph if file structure is unexpected
#     except FileNotFoundError:
#         print(f"File not found: {file_path}")
#         return px.bar(labels={"1": "Datum", "0": "Razina peludi"})  # Return an empty graph if file not found


app.run_server(debug=True)
