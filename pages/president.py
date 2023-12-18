from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import dash
import dash_bootstrap_components as dbc
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

connection = sqlite3.connect("./elections.db")


def drawFigure(figure):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                figure
            ])
        ),
    ])


def drawDropdown(dropdown):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div(
                    dropdown
                )
            ])
        ),
    ])


layout = html.Div([
    dbc.Button("Назад", style={'fontSize': '24px'}, href="/"),
    dbc.Card(
        dbc.CardBody([
            html.H1('Выборы в Госдуму'),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    drawDropdown([
                        html.Div(children='Год'),
                        dcc.Dropdown(
                            [2004, 2008, 2012, 2018],
                            2012,
                            id='year_dropdown')
                    ])
                ], width=3),
                dbc.Col([
                    drawDropdown([html.Div(children='Регион'),
                                  dcc.Dropdown(
                                      pd.read_sql_query('SELECT region_name FROM region', connection)['region_name'],
                                      'Вся Россия',
                                      id='region_dropdown')])
                ], width=3),
                dbc.Col([
                    drawDropdown([
                        html.Div(children='Отображать регионы по'),
                        dcc.Dropdown(
                            ['Явка'] + [f'Голоса за {cand}' for cand in
                                        pd.read_sql_query('SELECT candidate_name FROM p_candidate', connection)[
                                            'candidate_name']],
                            'Явка',
                            id='map_dropdown')
                    ])
                ], width=6)
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(dcc.Graph(figure={}, id='results')),
                    drawFigure(dcc.Graph(figure={}, id='turnout'))
                ], width=4),
                dbc.Col([
                    drawFigure(dcc.Graph(figure={}, id='map')),
                    dbc.Button(
                        "Вся Россия", id="reset", className="me-2", n_clicks=0
                    )
                ], width=8),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H2('Явка по регионам'),
                    html.Hr(),
                    drawDropdown([
                        dcc.Dropdown(
                            [2004, 2008, 2012, 2018],
                            2012,
                            id='year_dropdown_2')
                    ])
                ], width=6),
                dbc.Col([
                    html.H2('Предпочтения по регионам'),
                    html.Hr(),
                    drawDropdown([dcc.Dropdown(
                        pd.read_sql_query('SELECT region_name FROM region', connection)['region_name'],
                        'Вся Россия',
                        id='region_dropdown_2')
                    ])
                ], width=6),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(dcc.Graph(figure={}, id='turnout_best')),
                    drawFigure(dcc.Graph(figure={}, id='turnout_worst'))
                ], width=6),
                dbc.Col([
                    drawFigure(dcc.Graph(figure={}, id='cand_best')),
                    drawFigure(dcc.Graph(figure={}, id='cand_worst'))
                ], width=6),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H2('Показатели по кандидатам'),
                    html.Hr(),
                    drawDropdown([
                        dcc.Dropdown(
                            pd.read_sql_query('SELECT candidate_name FROM p_candidate', connection)['candidate_name'],
                            'Путин Владимир Владимирович',
                            id='p_candidate_dropdown')
                    ])
                ], width=12),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(dcc.Graph(figure={}, id='cand_top5'))
                ], width=6),
                dbc.Col([
                    drawFigure(dcc.Graph(figure={}, id='cand_worst5'))
                ], width=6)
            ], align='center'),
            dbc.Row([
                dbc.Col([
                    drawFigure(dcc.Graph(figure={}, id='cand_top5_reg'))
                ], width=6),
                dbc.Col([
                    drawFigure(dcc.Graph(figure={}, id='cand_worst5_reg'))
                ], width=6),
            ], align='center')
        ]), color='dark'
    )
])
