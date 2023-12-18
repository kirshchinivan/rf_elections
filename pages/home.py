from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
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
    path='',
    title='Начало',
    name='Начало'
)

layout = dbc.Container([
    html.H1('Выборы в России'),
    html.H3('Артем Уткин, Кирщин Иван'),
    html.Hr(),
    dbc.Row(dbc.Button("Выборы президента", style={'fontSize': '24px'}, href="/president")),
    html.Br(),
    dbc.Row(dbc.Button("Выборы в Госдуму", style={'fontSize': '24px'}, href="/parliament"))
])
