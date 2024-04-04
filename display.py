import os

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State

biljke = ["PITOMI_KESTEN", "KOPRIVE", "BOR", "TRAVE", "LIPA", "TRPUTAC", "MASLINA", "HRAST_CRNIKA", "CRKVINA",
          "CEMPRESI", "AMBROZIJA", "HRAST", "LOBODA", "HRAST_SP", "PELIN"]

# Define data directory
data_directory = "..\\ambrozija\data"

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


# Read data directory structure
cities, years, months = read_data_directory(data_directory)

app = Dash(__name__)

app.layout = html.Div([
    html.H2(children=f'Razina peludi:', style={'textAlign': 'center'}),
    html.Div(
        dcc.Dropdown(options=[{'label': city, 'value': city} for city in cities], id='city-dropdown',
                     disabled=False),
        style={'width': '25%', 'display': 'inline-block'}),
    html.Div(dcc.Dropdown(options=[], id='year-dropdown', disabled=True),
             style={'width': '25%', 'display': 'inline-block'}),
    html.Div(dcc.Dropdown(options=[], id='month-dropdown', disabled=True),
             style={'width': '25%', 'display': 'inline-block'}),
    html.Div(
        dcc.Dropdown(options=[], id='plant-dropdown', disabled=True),
        style={'width': '25%', 'display': 'inline-block'}),
    dcc.Graph(id="graph"),
    html.Div(id='warning-message', style={'textAlign': 'center', 'color': 'red'}),
    html.P(
        children='Izvor podataka: Nastavni zavod za javno zdravstvo \"Dr. Andrija Štampar\", https://stampar.hr/hr/peludna-prognoza',
        style={'textAlign': 'center'}),
])


# Callback to update year dropdown based on selected city
@app.callback(
    Output('year-dropdown', 'options'),
    [Input('city-dropdown', 'value')]
)
def update_years(city):
    if city:
        return [{'label': str(year), 'value': year} for year in years]
    else:
        return []


# Callback to update month dropdown based on selected year
@app.callback(
    [Output('month-dropdown', 'options'),
     Output('month-dropdown', 'disabled')],
    [Input('year-dropdown', 'value')]
)
def update_months(year):
    if year:
        return [{'label': str(month), 'value': month} for month in months], False
    else:
        return [], True


# Callback to update plant dropdown based on selected month
@app.callback(
    [Output('plant-dropdown', 'options'),
     Output('plant-dropdown', 'disabled')],
    [Input('month-dropdown', 'value')]
)
def update_plants(month):
    if month:
        return [{'label': plant, 'value': plant} for plant in biljke], False
    else:
        return [], True


# Callback function to update graph and warning message
@app.callback(
    [Output("graph", "figure"),
     Output("warning-message", "children")],
    [Input('plant-dropdown', 'value')],
    [State('city-dropdown', 'value'),
     State('year-dropdown', 'value'),
     State('month-dropdown', 'value')]
)
def display_graph_and_warning(plant, city, year, month):
    if plant and city and year and month:
        file_path = get_file_path(data_directory, city, plant, year, month)
        try:
            df = pd.read_csv(file_path, header=None, sep='  ', engine='python')
            if len(df.columns) >= 2:
                fig = px.bar(df, x=df.columns[1], y=df.columns[0], labels={"1": "Datum", "0": "Razina peludi"})
                return fig, None  # Return figure and no warning message if data is available
            else:
                return None, "Nema dostupnih podataka za odabrane parametre."  # Return no figure and warning message if data structure is unexpected
        except FileNotFoundError:
            return None, "Nema dostupnih podataka za odabrane parametre."  # Return no figure and warning message if file not found
    else:
        return None, None


if __name__ == '__main__':
    app.run_server(debug=True)
