from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import dash
import sqlite3

dash.register_page(
    __name__,
    path='/president',
    title='Президентские выборы',
    name='Президентские выборы'
)

connection = sqlite3.connect("./elections.db")


def draw_figure(figure):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                figure
            ])
        ),
    ])


def draw_dropdown(dropdown):
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
            html.H1('Президентские выборы'),
            html.Hr(),

            dbc.Row([
                dbc.Col([
                    draw_dropdown([
                        html.Div(children='Год'),
                        dcc.Dropdown(
                            [2004, 2008, 2012, 2018],
                            2018,
                            id='year_dropdown')
                    ])
                ], width=3),

                dbc.Col([
                    draw_dropdown([html.Div(children='Регион'),
                                   dcc.Dropdown(
                                       pd.read_sql_query('SELECT region_name FROM region', connection)['region_name'],
                                       'Вся Россия',
                                       id='region_dropdown')])
                ], width=3),

                dbc.Col([
                    draw_dropdown([
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
                    draw_figure(dcc.Graph(figure={}, id='results')),
                    draw_figure(dcc.Graph(figure={}, id='turnout'))
                ], width=4),

                dbc.Col([
                    draw_figure(dcc.Graph(figure={}, id='map')),
                    dbc.Button("Вся Россия", id="reset", className="me-2", n_clicks=0)
                ], width=8),
            ], align='center'),

            html.Br(),

            dbc.Row([
                dbc.Col([
                    html.H2('Явка по регионам'),
                    html.Hr(),
                    draw_dropdown([
                        dcc.Dropdown(
                            [2004, 2008, 2012, 2018],
                            2018,
                            id='year_dropdown_2')
                    ])
                ], width=6),

                dbc.Col([
                    html.H2('Предпочтения по регионам'),
                    html.Hr(),
                    draw_dropdown([dcc.Dropdown(
                        [reg + " " for reg in
                         pd.read_sql_query('SELECT region_name FROM region', connection)['region_name'].values],
                        'Вся Россия ',
                        id='region_dropdown_2')])
                ], width=6),
            ], align='center'),

            html.Br(),

            dbc.Row([
                dbc.Col([
                    draw_figure(dcc.Graph(figure={}, id='turnout_best')),
                    draw_figure(dcc.Graph(figure={}, id='turnout_worst'))
                ], width=6),

                dbc.Col([
                    draw_figure(dcc.Graph(figure={}, id='cand_best')),
                    draw_figure(dcc.Graph(figure={}, id='cand_worst'))
                ], width=6),
            ], align='center'),

            html.Br(),

            dbc.Row([
                dbc.Col([
                    html.H2('Показатели по кандидатам'),
                    html.Hr(),
                    draw_dropdown([
                        dcc.Dropdown(
                            pd.read_sql_query('SELECT candidate_name FROM p_candidate', connection)['candidate_name'],
                            'Путин Владимир Владимирович',
                            id='candidate_dropdown')
                    ])
                ], width=12)
            ], align='center'),

            html.Br(),

            dbc.Row([
                dbc.Col([
                    draw_figure(dcc.Graph(figure={}, id='cand_top5'))
                ], width=6),

                dbc.Col([
                    draw_figure(dcc.Graph(figure={}, id='cand_worst5'))
                ], width=6)
            ], align='center'),

            dbc.Row([
                dbc.Col([
                    draw_figure(dcc.Graph(figure={}, id='cand_top5_reg'))
                ], width=6),

                dbc.Col([
                    draw_figure(dcc.Graph(figure={}, id='cand_worst5_reg'))
                ], width=6),
            ], align='center')
        ]), color='dark'
    )
])
