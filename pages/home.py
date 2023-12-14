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
    path='',
    title='Начало',
    name='Начало'
)

layout = html.Div([
    dcc.Link(html.Button("Выборы президента"), href="/president"),
    dcc.Link(html.Button("Выборы в Госдуму"), href="/parliament")
])

