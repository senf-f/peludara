import os

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State

from display import biljke

# Define data directory
data_directory = "..\\ambrozija\data"

app = Dash(__name__)


# Function to read data directory structure and extract cities, years, and months
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

app.layout = html.Div([
    html.H1(children='Razina peludi:', style={'textAlign': 'center'}),
    html.Div([html.P(children="Grad"),
              dcc.Dropdown(options=[{'label': city, 'value': city} for city in cities], id='city-dropdown',
                           disabled=False, style={'width': '90%'})],
             style={'display': 'flex', 'justify-content': 'space-evenly'}),
    html.Div([html.P(children="Godina"),
              dcc.Dropdown(options=[{'label': year, 'value': year} for year in years], id='year-dropdown',
                           disabled=True, style={'width': '90%'})],
             style={'display': 'flex', 'justify-content': 'space-evenly'}),
    html.Div([html.P(children="Biljka"),
              dcc.Dropdown(options=[{'label': plant, 'value': plant} for plant in biljke], id='plant-dropdown',
                           disabled=True, style={'width': '90%'})],
             style={'display': 'flex', 'justify-content': 'space-evenly'}),
    html.Div([html.P(children="Mjesec"),
              dcc.Dropdown(options=[{'label': month, 'value': month} for month in months], id='month-dropdown',
                           disabled=True, style={'width': '90%'})],
             style={'display': 'flex', 'justify-content': 'space-evenly'}),
    dcc.Graph(id="graph"),
    html.P(
        children='Izvor podataka: Nastavni zavod za javno zdravstvo \"Dr. Andrija Štampar\", https://stampar.hr/hr/peludna-prognoza',
        style={'textAlign': 'center'}),
    html.Div(id="warning-message"),
    # html.Div(id='placeholder')
])

# Callback function to update the options of the plant dropdown based on selected city and year
@app.callback(
    Output('plant-dropdown', 'options'),
    Input('year-dropdown', 'value'),
    State('city-dropdown', 'value'),
    prevent_initial_call=True
)
def update_plant_dropdown(selected_year, city):
    if city is None or selected_year is None:
        return []

    # Extract plants associated with the selected city and year
    city_year_plants = set()
    for month_folder in os.listdir(os.path.join(data_directory, str(selected_year))):
        for file_name in os.listdir(os.path.join(data_directory, str(selected_year), month_folder)):
            parts = file_name.split(' pelud za ')[0].split(' - ')
            if len(parts) == 2 and parts[0] == city:
                city_year_plants.add(parts[1])

    plant_options = [{'label': plant, 'value': plant} for plant in sorted(city_year_plants)]

    return plant_options


# Callback function to update graph and warning message
@app.callback(
    [Output("graph", "figure"),
     Output("warning-message", "children")],  # Output for the warning message
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
        return px.bar(pd.DataFrame(columns=['Datum', 'Razina peludi'])), None  # Return empty figure and no warning message if parameters are not selected



if __name__ == '__main__':
    app.run_server(debug=True)
