from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import json
from ScrapingProff.NACEs import NACE_2025_kunder
import plotly.express as px

"""
For loading initially. This is where the economic data, the geodata and the industry names are loaded.
"""
tables = {
    " ".join(branche.split()[1:]):pd.read_csv("DashboardProffData/BrancheDatasætTilBrug/"+" ".join((branche.split()[1:])).replace(' ','_')+".csv") for branche in NACE_2025_kunder
}
brancher = [" ".join(x.split()[1:]) for x in NACE_2025_kunder]
with open('municipalities_for_python.geojson') as geo_json:
        geom_data = json.load(geo_json)

"""
Functionality used for datahandling for the map.
"""
def filter_industries(data,columns):
    if columns:
        as_queries = [f"`{column}` == 1" for column in columns]
        query = " or ".join(as_queries)
        data = data.query(query)
    return data

def process_from_category_map(data,category):
     if category == 'Omsætning':
         return data[['Kommune','Bruttofortjeneste']].groupby(by='Kommune').sum().reset_index(), 'Bruttofortjeneste'
     if category == 'Antal virksomheder':
          data = data['Kommune'].value_counts().reset_index()
          data.columns = ['Kommune','Antal virksomheder']
          return data, 'Antal virksomheder'
     if category == 'Kunder':
        return data[['Kommune','Kunde']].groupby(by='Kommune').sum().reset_index(), 'Kunde'
     if category == 'Coating kunder':
        return data[['Kommune','Coating kunde']].groupby(by='Kommune').sum().reset_index(), 'Coating kunde'

"""
Functionality used for datahandling for the histogram.
"""
def process_from_category_graph(data,category):
     if category == 'Omsætning':
         return data['Bruttofortjeneste'], 'Bruttofortjeneste'
     if category == 'Antal virksomheder':
          data = data['Kommune'].value_counts().reset_index()
          data.columns = ['Kommune','Antal virksomheder']
          return data, 'Antal virksomheder'
     if category == 'Kunder':
        return data[['Kommune','Kunde']].groupby(by='Kommune').sum().reset_index(), 'Kunde'
     if category == 'Coating kunder':
        return data[['Kommune','Coating kunde']].groupby(by='Kommune').sum().reset_index(), 'Coating kunde'

"""
Layout.
"""
app = Dash()

selection_width = '5in'

app.layout = [
    html.H1(children='Dashboard til markedsundersøgelse'),
    html.Div(children=[
        html.Div(children=[
            html.Label('Vælg branche:', style={"font-weight": "bold"}),
            dcc.Dropdown(brancher, brancher[0], id='branche', clearable=False)
        ],style={'padding-bottom':'0.2in','width':'4in'}),
        html.Div(children=[
            html.Label('Vælg kategori:', style={"font-weight": "bold"}),
            dcc.Dropdown(['Omsætning', 'Antal virksomheder', 'Kunder', 'Coating kunder'], 'Omsætning', id='kategori', multi=False)
        ],style={'padding-bottom':'0.2in','width':'2in'}),
        html.Div(children=[
            html.Label('Vælg underbrancher:', style={"font-weight": "bold"}),
            dcc.Dropdown(brancher, None, id='underbrancher', multi=True)
        ],style={'padding-bottom':'0.2in','width':'9in'}),
    ],style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div(children=[
        dcc.Graph(id='kortet',style={})
    ], style={"border":"2px black solid"}),
    html.Div(children=[
        dash_table.DataTable(id='tabel',page_size=10,sort_action='custom',
                         sort_mode='single',sort_by=[],filter_action='custom',filter_query='')
    ], style={"padding-top":"10px"}), 
]

"""
Callbacks.
"""
@callback(
    Output('underbrancher', 'options'),
    Output('underbrancher', 'value'),
    Input('branche', 'value')
)
def find_rigtige_brancher(branche):
    table = tables[branche]
    return table.columns[15:], table.columns[15:]

@callback(
    Output('kortet', 'figure'),
    Input('branche', 'value'),
    Input('underbrancher', 'value'),
    Input('kategori', 'value'),
)
def lav_kort(branche,underbrancher,kategori):
    if underbrancher:
        data = tables[branche]
        data = filter_industries(data,underbrancher)
        data, color = process_from_category_map(data,kategori)
        fig = px.choropleth(data_frame=data, geojson=geom_data,locations='Kommune',featureidkey='properties.label_dk',
                        color=color, color_continuous_scale="greens",height=700)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}), fig.update_geos(fitbounds="locations", visible=False)
        return fig
    else:
         return px.choropleth()

@callback(
    Output('tabel', 'data'),
    Output('tabel','columns'),
    Input('branche', 'value'),
    Input('underbrancher', 'value'),
    Input('tabel', 'sort_by'),
    Input('tabel', 'filter_query')
)
def opdater_tabel(branche,underbrancher,sorter,filtrer):
    data = tables[branche]
    data = filter_industries(data,underbrancher)
    data = data.iloc[:,:15]
    data = data[['Juridisk navn', 'Kommune', 'Antal ansatte', 'Bruttofortjeneste', 'Valuta', 'År for beregning', 'Kunde', 'Coating kunde']]
    if sorter:
        sorter = sorter.pop()
        data = data.sort_values(by=sorter['column_id'],ascending=('asc'==sorter['direction']))
    if filtrer:
        column, term = filtrer.split(" scontains ")
        column = "".join(column.split('{')).split("}").pop(0)
        data = data.loc[data[column].str.contains(term)]
    return data.to_dict('records'), [{"name": i, 'id': i} for i in data.columns]

# @callback(
#     Output('grafen', 'figure'),
#     Input('branche', 'value'),
#     Input('kategori', 'value'),
# )
# def lav_graf(branche,kategori):
#     data = tables[branche]
#     data, color = process_from_category_graph(data,kategori)
#     return px.histogram(data_frame=data,x=color)

server = app.server

if __name__ == '__main__':
    app.run(debug=True)
