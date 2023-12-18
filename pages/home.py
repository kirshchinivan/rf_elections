from dash import html
import dash_bootstrap_components as dbc
import dash

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
