from dash import html, dcc
import dash_bootstrap_components as dbc
import dash

dash.register_page(
    __name__,
    path="",
    title="Начало",
    name="Начало"
)


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


layout = dbc.Container([
    html.H1("Выборы в России"),
    html.H3("Кирщин Иван, Артем Уткин"),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            draw_dropdown([
                html.Div(children="Результаты за все время", style={"fontSize": "24px"}),
                dcc.RangeSlider(2003, 2018, 1, value=[2003, 2018],
                                marks={i: "{}".format(i) for i in [2003, 2004, 2007, 2008, 2011, 2012, 2018]},
                                id="years"),
            ])
        ], width=12)
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            draw_figure(dcc.Graph(figure={}, id="gd_years_results")),
        ], width=6),
        dbc.Col([
            draw_figure(dcc.Graph(figure={}, id="p_years_results")),
        ], width=6)
    ]),
    html.Br(),
    dbc.Row(dbc.Button("Выборы президента", style={"fontSize": "24px"}, href="/president")),
    html.Br(),
    dbc.Row(dbc.Button("Выборы в Госдуму", style={"fontSize": "24px"}, href="/parliament")),
    html.Br()
])
