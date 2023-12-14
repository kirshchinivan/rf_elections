from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import dash
import json
import sqlite3
import plotly as plt
import zipfile
from urllib.request import urlopen
import sys
import pathlib

dash.register_page(
    __name__,
    path='/president',
    title='Президентские выборы',
    name='Президентские выборы'
)

connection = sqlite3.connect("elections.db")


layout = html.Div([
    dcc.Link(html.Button("Назад"), href="/"),
    html.Div(children='Выберите регион'),
    dcc.Dropdown(pd.read_sql_query('SELECT region_name FROM region', connection)['region_name'],
                 'Вся Россия',
                 id='region_dropdown'),
    html.Div(children='Выберите год'),
    dcc.Dropdown(
        [2004, 2008, 2012, 2018],
        2012,
        id='year_dropdown'),
    html.Div(children='Отображать регионы по'),
    dcc.Dropdown(
        ['Явка'] + [f'Голоса за {cand}' for cand in
                    pd.read_sql_query('SELECT candidate_name FROM p_candidate', connection)['candidate_name']],
        'Явка',
        id='map_dropdown'),
    dcc.Graph(figure={}, id='map', style={'display': 'inline-block'}),
    html.Div(children=[
        dcc.Graph(figure={}, id='results', style={'display': 'inline-block'}),
        dcc.Graph(figure={}, id='turnout', style={'display': 'inline-block'})
    ]),
    html.H2("Межрегиональные показатели"),
    html.Hr(),
    dcc.Dropdown(
        [2004, 2008, 2012, 2018],
        2012,
        id='year_dropdown_2'),
    html.Div(children=[
        dcc.Graph(figure={}, id='turnout_best', style={'display': 'inline-block'}),
        dcc.Graph(figure={}, id='turnout_worst', style={'display': 'inline-block'})
    ]),
    html.H2("Показатели по кандидатам"),
    html.Hr(),
    dcc.Dropdown(
        pd.read_sql_query('SELECT candidate_name FROM p_candidate', connection)['candidate_name'],
        'Путин Владимир Владимирович',
        id='p_candidate_dropdown'),
    html.Div(children=[
        dcc.Graph(figure={}, id='perc_results', style={'display': 'inline-block'}),
        dcc.Graph(figure={}, id='abs_results', style={'display': 'inline-block'})
    ]),
    html.Div(children=[
        dcc.Graph(figure={}, id='cand_top5', style={'display': 'inline-block'}),
        dcc.Graph(figure={}, id='cand_worst5', style={'display': 'inline-block'})
    ]),
])