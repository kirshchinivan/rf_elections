from dash import html, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import dash
import json
import sqlite3

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SLATE])
server = app.server

# Открываем geojson
with open("russia.geojson", encoding="UTF-8") as response:
    counties = json.load(response)

# Определяем область, в которой будет находиться текущая страница
app.layout = html.Div([
    dash.page_container
])


# Строим графики суммарного количества набранных кандидатами голосов за годы, выбранные на слайдере
@callback(
    [Output("p_years_results", "figure"),
     Output("gd_years_results", "figure")],
    Input("years", "value")
)
def update_graph(years):
    # Подключаемся к БД
    connection = sqlite3.connect("elections.db")

    # Находим суммарное количество голосов за выбранный период для кандидатов в президенты
    data_p = pd.read_sql_query(f"""
        SELECT candidate_name, SUM(votes) as votes
        FROM 
            president_elections_cand
            INNER JOIN p_candidate USING(candidate_id)
        WHERE year >= {years[0]} AND year <= {years[1]} AND region_id = (
            SELECT region_id
            FROM region
            WHERE region_name = "Вся Россия"
        )
        GROUP BY candidate_id
        HAVING SUM(votes) * 1.0 / (
            SELECT SUM(votes)
            FROM president_elections_cand
            WHERE year >= {years[0]} AND year <= {years[1]}
        ) >= 0.02
        UNION
        SELECT "Все остальные (< 2%)", SUM(votes)
        FROM (
                SELECT SUM(votes) as votes
                FROM 
                    president_elections_cand
                    INNER JOIN p_candidate USING(candidate_id)
                WHERE year >= {years[0]} AND year <= {years[1]} AND region_id = (
                    SELECT region_id
                    FROM region
                    WHERE region_name = "Вся Россия"
                )
                GROUP BY candidate_id
                HAVING SUM(votes) * 1.0 / (
                    SELECT SUM(votes)
                    FROM president_elections_cand
                    WHERE year >= {years[0]} AND year <= {years[1]}
                ) < 0.02
            ) another;
    """, connection)

    # Находим суммарное количество голосов за выбранный период для партий-кандидатов в Госдуму
    data_gd = pd.read_sql_query(f"""
        SELECT candidate_name, SUM(votes) as votes
        FROM 
            gd_elections_cand
            INNER JOIN gd_candidate USING(candidate_id)
        WHERE year >= {years[0]} AND year <= {years[1]} AND region_id = (
            SELECT region_id
            FROM region
            WHERE region_name = "Вся Россия"
        )
        GROUP BY candidate_id
        HAVING SUM(votes) * 1.0 / (
            SELECT SUM(votes)
            FROM gd_elections_cand
            WHERE year >= {years[0]} AND year <= {years[1]}
        ) >= 0.02
        UNION
        SELECT "Все остальные (< 2%)", SUM(votes)
        FROM (
                SELECT SUM(votes) as votes
                FROM 
                    gd_elections_cand
                    INNER JOIN gd_candidate USING(candidate_id)
                WHERE year >= {years[0]} AND year <= {years[1]} AND region_id = (
                    SELECT region_id
                    FROM region
                    WHERE region_name = "Вся Россия"
                )
                GROUP BY candidate_id
                HAVING SUM(votes) * 1.0 / (
                    SELECT SUM(votes)
                    FROM gd_elections_cand
                    WHERE year >= {years[0]} AND year <= {years[1]}
                ) < 0.02
            ) another;
    """, connection)

    # Строим pie plot для кандидатов в президенты
    fig1 = px.pie(data_p, values="votes", names="candidate_name", hole=0.6,
                  title=f"Суммарное количество голосов с {years[0]} по {years[1]}")
    # Настраиваем информацию, показывающуюся при наведении курсора на график
    fig1.update_traces(
        hovertemplate="<br>".join([
            "%{label}",
            "Суммарное количество голосов: %{value}"
        ])
    )
    # Настраиваем цвет фона графика в соответствии с цветом страницы
    fig1.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )

    # Строим pie plot для партий-кандидатов в Госдуму
    fig2 = px.pie(data_gd, values="votes", names="candidate_name", hole=0.6,
                  title=f"Суммарное количество голосов с {years[0]} по {years[1]}")
    # Настраиваем информацию, показывающуюся при наведении курсора на график
    fig2.update_traces(
        hovertemplate="<br>".join([
            "%{label}",
            "Количество голосов: %{value}"
        ])
    )
    # Настраиваем цвет фона графика в соответствии с цветом страницы
    fig2.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )

    return fig1, fig2


# Согласовываем выпадающий список с форматами отображения карты со списком с годами выборов
@callback(
    [Output("map_dropdown", "options"),
     Output("map_dropdown", "value")],
    [Input("year_dropdown", "value"),
     Input("map_dropdown", "value")]
)
def update_options(year, param):
    # Подключаемся к БД
    connection = sqlite3.connect("elections.db")

    # Так как графики для обоих выборов у нас общие, нужно понимать, с какими именно выборами мы сейчас работаем
    if year in [2003, 2007, 2011]:
        candidates = "gd"
        elections = "gd"
    else:
        candidates = "p"
        elections = "president"

    # Находим кандидатов, участвовавших в выборах в указанный год
    candidates = pd.read_sql_query(f"""
        SELECT candidate_name
        FROM (
            SELECT DISTINCT candidate_id
            FROM {elections}_elections_cand
            WHERE year = {year}
            ) cand_ids
            INNER JOIN {candidates}_candidate USING(candidate_id)
    """, connection)["candidate_name"].values

    # Создаем список из всех доступных форматов отображения карты в выбранный год
    options = ["Явка"] + [f"Голоса за {cand}" for cand in candidates]
    if param not in options:
        param = "Явка"

    return options, param


# Рисуем карту регионов России в соответствии с выбранными форматом отображения, годом и регионом
@callback(
    Output("map", "figure"),
    [Input("map_dropdown", "value"),
     Input("year_dropdown", "value"),
     Input("region_dropdown", "value")]
)
def update_graph(param, year, region):
    # Подключаемся к БД
    connection = sqlite3.connect("elections.db")

    # Определяем, с какими выборами мы имеем дело
    if year in [2003, 2007, 2011]:
        candidates = "gd"
        elections = "gd"
    else:
        candidates = "p"
        elections = "president"

    # Обрабатываем случай, когда никакой регион не выбран (то есть, в качестве региона выбрана вся Россия
    if region == "Вся Россия":
        # Обрабатываем случай, когда выбрано отображение регионов по явке
        if param == "Явка":
            # Считаем явку для каждого региона
            data = pd.read_sql_query(f"""
                SELECT region_id, region_name, ROUND(came * 1.0 / voters * 100, 2) AS turnout
                FROM 
                    {elections}_elections_region 
                    INNER JOIN region USING(region_id)
                WHERE year = {year} AND region_id <> (
                    SELECT region_id
                    FROM region
                    WHERE region_name = "Вся Россия"
                )
            """, connection)

            # Рисуем карту России, на которой подсвечиваем регионы в соответствии с уровнем явки
            fig = px.choropleth_mapbox(data, geojson=counties, locations="region_id", color="turnout",
                                       color_continuous_scale="deep",
                                       range_color=(0, 100),
                                       mapbox_style="carto-positron",
                                       zoom=1.25, center={"lat": 70, "lon": 94},
                                       hover_data="region_name", custom_data=["region_name", "turnout"],
                                       labels={"turnout": "Явка"})
            # Настраиваем информацию, показывающуюся при наведении курсора на карту
            fig.update_traces(
                hovertemplate="<br>".join([
                    "%{customdata[0]}",
                    "Явка: %{customdata[1]}%"
                ])
            )
        # Обрабатываем случай, когда выбрано отображение регионов по голосам за одного из кандидатов
        else:
            # Определяем выбранного кандидата
            param = param[10:]

            # Считаем процент голосов за выбранного кандидата в каждом из регионов
            data = pd.read_sql_query(f"""
                SELECT ec.region_id, region_name, ROUND(votes * 1.0 / voted * 100, 2) AS perc
                FROM 
                    {elections}_elections_cand AS ec
                    INNER JOIN {elections}_elections_region AS er ON ec.region_id = er.region_id AND ec.year = er.year
                    INNER JOIN region USING(region_id)
                WHERE ec.year = {year} AND ec.region_id <> (
                    SELECT region_id
                    FROM region
                    WHERE region_name = "Вся Россия"
                ) AND candidate_id = (
                    SELECT candidate_id
                    FROM {candidates}_candidate
                    WHERE candidate_name = "{param}"
                )
            """, connection)

            # Рисуем карту России, на которой подсвечиваем регионы в соответствии с количеством голосов
            fig = px.choropleth_mapbox(data, geojson=counties, locations="region_id", color="perc",
                                       color_continuous_scale="deep",
                                       range_color=(0, 100),
                                       mapbox_style="carto-positron",
                                       zoom=1.25, center={"lat": 70, "lon": 94},
                                       hover_data="region_name", custom_data=["region_name", "perc"],
                                       labels={"perc": f"Голоса"})
            # Настраиваем информацию, показывающуюся при наведении курсора на карту
            fig.update_traces(
                hovertemplate="<br>".join([
                    "%{customdata[0]}",
                    "Процент голосов: %{customdata[1]}%"
                ])
            )
    # Обрабатываем случай, когда выбран один из регионов
    else:
        # Создаем таблицу, в которой отмечаем выбранный регион
        data = pd.read_sql_query(f"""
            SELECT region_id, region_name, CASE WHEN region_name = "{region}" THEN 100 ELSE 0 END AS color
            FROM region
            """, connection)

        # Рисуем карту, на которой выделен выбранный регион
        fig = px.choropleth_mapbox(data, geojson=counties, locations="region_id", color="color",
                                   color_continuous_scale="reds",
                                   range_color=(0, 100),
                                   mapbox_style="carto-positron",
                                   zoom=1.25, center={"lat": 70, "lon": 94},
                                   hover_data="region_name", custom_data=["region_name"])
        # Настраиваем информацию, показывающуюся при наведении курсора на карту
        fig.update_traces(
            hovertemplate="%{customdata[0]}"
        )
        # Скрываем colorbar, который в данном случае не имеет никакого смысле
        fig.update_layout(coloraxis_showscale=False)

    # Настраиваем фон карты, ее размер и способ отображения выбранного показателя
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        height=550,
        coloraxis_colorbar={"ticksuffix": "%"}
    )

    return fig


# Обрабатываем клики по карте и нажатие кнопки "Вся Россия"
@callback(
    [Output("region_dropdown", "value"),
     Output("reset", "n_clicks")],
    [Input("map", "clickData"),
     Input("reset", "n_clicks")]
)
def update_region(clickData, n_clicks):
    # Обрабатываем случай, когда нажатия на карту не было
    if clickData is None:
        return "Вся Россия", 0

    # Обрабатываем случай, когда была нажата кнопка "Вся Россия"
    if n_clicks > 0:
        return "Вся Россия", 0

    # Иначе возвращаем регион, на который кликнул пользователь
    return clickData["points"][0]["customdata"][0], 0


# Строим pie plot для результатов выборов и явки на выборах в выбранном регионе в выбранный год
@callback(
    [Output("results", "figure"),
     Output("turnout", "figure")],
    [Input("region_dropdown", "value"),
     Input("year_dropdown", "value")]
)
def update_graph(region, year):
    # Подключаемся к БД
    connection = sqlite3.connect("elections.db")

    # Определяем, с какими выборами мы имеем дело
    if year in [2003, 2007, 2011]:
        candidates = "gd"
        elections = "gd"
    else:
        candidates = "p"
        elections = "president"

    # Создаем таблицу с результатами кандидатов в выбранном регионе в выбранный год
    data1 = pd.read_sql_query(f"""
        SELECT candidate_name, votes
        FROM 
            {elections}_elections_cand
            INNER JOIN {candidates}_candidate USING(candidate_id)
        WHERE year = {year} AND region_id = (
            SELECT region_id
            FROM region
            WHERE region_name = "{region}"
            ) AND votes * 1.0 / (
                SELECT SUM(votes)
                FROM {elections}_elections_cand
                WHERE year = {year} AND region_id = (
                    SELECT region_id
                    FROM region
                    WHERE region_name = "{region}"
                    )
            ) >= 0.05
        UNION
        SELECT "Все остальные (< 5%)", SUM(votes)
        FROM 
            {elections}_elections_cand
            INNER JOIN {candidates}_candidate USING(candidate_id)
        WHERE year = {year} AND region_id = (
            SELECT region_id
            FROM region
            WHERE region_name = "{region}"
            ) AND votes * 1.0 / (
                SELECT SUM(votes)
                FROM {elections}_elections_cand
                WHERE year = {year} AND region_id = (
                    SELECT region_id
                    FROM region
                    WHERE region_name = "{region}"
                    )
            ) < 0.05
    """, connection)

    # Создаем таблицу с информацией о явке в выбранном регионе в выбранный год
    data2 = pd.read_sql_query(f"""
        SELECT voted, came - voted AS not_voted, voters - came AS not_came
        FROM {elections}_elections_region
        WHERE year = {year} AND region_id = (
            SELECT region_id
            FROM region
            WHERE region_name = "{region}"
            )
    """, connection)

    # Строим pie plot для итогов выборов
    fig1 = px.pie(data1, values="votes", names="candidate_name",
                  title=f"Итоги голосования")
    # Настраиваем информацию, показывающуюся при наведении курсора на график
    fig1.update_traces(
        hovertemplate="<br>".join([
            "%{label}",
            "Количество голосов: %{value}"
        ])
    )
    # Меняем цвет фона графика в соответствии с цветом страницы и настраиваем размер графика
    fig1.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        height=300
    )

    # Строим pie plot для информации о пришедших и не пришедших на выборы
    fig2 = px.pie(values=[data2["voted"][0], data2["not_voted"][0], data2["not_came"][0]],
                  names=["Проголосовали", "Пришли, но не проголосовали", "Не пришли"],
                  title=f"Явка")
    # Настраиваем информацию, показывающуюся при наведении курсора на график
    fig2.update_traces(
        hovertemplate="<br>".join([
            "%{label}",
            "%{value}"
        ])
    )
    # Меняем цвет фона графика в соответствии с цветом страницы и настраиваем размер графика
    fig2.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        height=300
    )

    return fig1, fig2


# Строим графики для лучших и худших по явке регионов в выбранный год
@callback(
    [Output("turnout_best", "figure"),
     Output("turnout_worst", "figure")
     ],
    Input("year_dropdown_2", "value")
)
def update_graph(year):
    # Подключаемся к БД
    connection = sqlite3.connect("elections.db")

    # Определяем, с какими выборами мы имеем дело
    if year in [2003, 2007, 2011]:
        elections = "gd"
    else:
        elections = "president"

    # Находим 5 лучших по явке регионов в выбранный год
    top5_turnout = pd.read_sql_query(f"""
        SELECT region_name, turnout, CASE WHEN region_name = "Вся Россия" THEN "r" ELSE "b" END AS color
        FROM
            (
                SELECT *
                FROM
                (
                    SELECT region_id, ROUND(came * 1.0 / voters * 100, 2) AS turnout
                    FROM {elections}_elections_region
                    WHERE year = {year} AND region_id <> (
                    SELECT region_id
                    FROM region
                    WHERE region_name = "Вся Россия"
                )
                    ORDER BY turnout DESC
                    LIMIT 5
                ) best_ids
                UNION
                SELECT region_id, ROUND(came * 1.0 / voters * 100, 2) AS turnout
                FROM {elections}_elections_region
                WHERE year = {year} AND region_id = (
                    SELECT region_id
                    FROM region
                    WHERE region_name = "Вся Россия"
                )
            ) AS region_ids
            INNER JOIN region USING(region_id)
            ORDER BY turnout DESC;
    """, connection)

    # Находим 5 худших по явке регионов в выбранный год
    worst5_turnout = pd.read_sql_query(f"""
        SELECT region_name, turnout, CASE WHEN region_name = "Вся Россия" THEN "r" ELSE "b" END AS color
        FROM
            (
                SELECT *
                FROM
                (
                    SELECT region_id, ROUND(came * 1.0 / voters * 100, 2) AS turnout
                    FROM {elections}_elections_region
                    WHERE year = {year} AND region_id <> (
                    SELECT region_id
                    FROM region
                    WHERE region_name = "Вся Россия"
                )
                    ORDER BY turnout
                    LIMIT 5
                ) best_ids
                UNION
                SELECT region_id, ROUND(came * 1.0 / voters * 100, 2) AS turnout
                FROM {elections}_elections_region
                WHERE year = {year} AND region_id = (
                    SELECT region_id
                    FROM region
                    WHERE region_name = "Вся Россия"
                )
            ) AS region_ids
            INNER JOIN region USING(region_id)
            ORDER BY turnout;
    """, connection)

    go.Figure(layout={"template": "plotly"})

    # Строим столбчатую диаграмму для 5 лучших по явке регионов в выбранный год
    fig1 = px.bar(top5_turnout, x="region_name", y="turnout", color="color",
                  title="Лучшие по явке регионы в выбранный год", labels={"region_name": "Регион", "turnout": "Явка"},
                  custom_data=["region_name", "turnout"])
    # Настраиваем информацию, показывающуюся при наведении курсора на график
    fig1.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Явка: %{customdata[1]}%<extra></extra>"
        ])
    )
    # Немного обрезаем названия регионов для того, чтобы график не съезжал
    fig1.update_xaxes(labelalias={reg: reg[:15] for reg in top5_turnout["region_name"].values})
    # Фиксируем границы для вертикальной оси
    fig1.update_yaxes(range=[0, 100])
    # Меняем цвет фона графика в соответствии с цветом страницы и скрываем легенду
    fig1.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        showlegend=False
    )

    # Строим столбчатую диаграмму для 5 худших по явке регионов в выбранный год
    fig2 = px.bar(worst5_turnout, x="region_name", y="turnout", color="color",
                  title="Худшие по явке регионы в выбранный год",
                  labels={"region_name": "Регион", "turnout": "Явка"},
                  custom_data=["region_name", "turnout"])
    # Настраиваем информацию, показывающуюся при наведении курсора на график
    fig2.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Явка: %{customdata[1]}%<extra></extra>"
        ])
    )
    # Немного обрезаем названия регионов для того, чтобы график не съезжал
    fig2.update_xaxes(labelalias={reg: reg[:15] for reg in worst5_turnout["region_name"].values})
    # Фиксируем границы для вертикальной оси
    fig2.update_yaxes(range=[0, 100])
    # Меняем цвет фона графика в соответствии с цветом страницы и скрываем легенду
    fig2.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        showlegend=False
    )

    return fig1, fig2


# Строим графики для самых любимых и самых нелюбимых кандидатов в выбранном регионе
@callback(
    [Output("cand_best", "figure"),
     Output("cand_worst", "figure")],
    Input("region_dropdown_2", "value")
)
def update_graph(region):
    # Подключаемся к БД
    connection = sqlite3.connect("elections.db")

    # Определяем, с какими выборами мы имеем дело
    if region[-1] == " ":
        candidates = "gd"
        elections = "gd"
    else:
        candidates = "p"
        elections = "president"
    region = region.strip()

    # Находим 5 самых любимых кандидатов в выбранном регионе по среднему проценту голосов
    data1 = pd.read_sql_query(f"""
        SELECT *
        FROM
        (
            SELECT candidate_name, ec.region_id, ROUND(SUM(votes * 1.0 / voted * 100) / COUNT(DISTINCT ec.year), 2) AS avg_perc
            FROM 
                {elections}_elections_cand AS ec
                INNER JOIN {elections}_elections_region AS er ON ec.region_id = er.region_id AND ec.year = er.year
                INNER JOIN {candidates}_candidate USING(candidate_id)
            WHERE ec.region_id = (
                SELECT region_id
                FROM region
                WHERE region_name = "{region}"
            )
            GROUP BY ec.region_id, candidate_id
            ORDER BY avg_perc DESC
            LIMIT 5
        ) region_ids INNER JOIN region USING(region_id)
    """, connection)

    # Находим 5 самых нелюбимых кандидатов в выбранном регионе по среднему проценту голосов
    data2 = pd.read_sql_query(f"""
        SELECT candidate_name, ec.region_id, ROUND(SUM(votes * 1.0 / voted * 100) / COUNT(DISTINCT ec.year), 2) AS avg_perc
        FROM 
            {elections}_elections_cand AS ec
            INNER JOIN {elections}_elections_region AS er ON ec.region_id = er.region_id AND ec.year = er.year
            INNER JOIN {candidates}_candidate USING(candidate_id)
        WHERE ec.region_id = (
            SELECT region_id
            FROM region
            WHERE region_name = "{region}"
        )
        GROUP BY ec.region_id, candidate_id
        ORDER BY avg_perc
        LIMIT 5
    """, connection)

    # Строим столбчатую диаграмму для 5 самых любимых кандидатов в выбранном регионе
    fig1 = px.bar(data1, x="candidate_name", y="avg_perc",
                  title="Самые любимые кандидаты в данном регионе",
                  custom_data=["candidate_name", "avg_perc"],
                  labels={"candidate_name": "Кандидат", "avg_perc": "Средний процент голосов за кандидата"})
    # Немного обрезаем имена кандидатов для того, чтобы график не съезжал
    fig1.update_xaxes(labelalias={cand: cand[:15] for cand in data1["candidate_name"].values})
    # Фиксируем границы для вертикальной оси
    fig1.update_yaxes(range=[0, 100])
    # Настраиваем информацию, показывающуюся при наведении курсора на график
    fig1.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Средний процент голосов в регионе: %{customdata[1]}%<extra></extra>"
        ])
    )
    # Меняем цвет фона графика в соответствии с цветом страницы
    fig1.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    # Строим столбчатую диаграмму для 5 самых нелюбимых кандидатов в выбранном регионе
    fig2 = px.bar(data2, x="candidate_name", y="avg_perc",
                  title="Самые нелюбимые кандидаты в данном регионе",
                  custom_data=["candidate_name", "avg_perc"],
                  labels={"candidate_name": "Кандидат", "avg_perc": "Средний процент голосов за кандидата"})
    # Немного обрезаем имена кандидатов для того, чтобы график не съезжал
    fig2.update_xaxes(labelalias={cand: cand[:15] for cand in data2["candidate_name"].values})
    # Настраиваем информацию, показывающуюся при наведении курсора на график
    fig2.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Средний процент голосов в регионе: %{customdata[1]}%<extra></extra>"
        ])
    )
    # Фиксируем границы для вертикальной оси
    fig2.update_yaxes(range=[0, 5])
    # Меняем цвет фона графика в соответствии с цветом страницы
    fig2.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    return fig1, fig2


# Строим графики для статистик по кандидату
@callback(
    [Output("cand_top5", "figure"),
     Output("cand_worst5", "figure"),
     Output("cand_top5_reg", "figure"),
     Output("cand_worst5_reg", "figure")],
    Input("candidate_dropdown", "value")
)
def update_graph(candidate):
    # Подключаемся к БД
    connection = sqlite3.connect("elections.db")

    # Определяем, с какими выборами мы имеем дело
    if candidate in pd.read_sql_query("SELECT candidate_name FROM gd_candidate", connection)["candidate_name"].values:
        candidates = "gd"
        elections = "gd"
    else:
        candidates = "p"
        elections = "president"

    # Находим 5 лучших результатов кандидата по всем регионам за все выборы
    data1 = pd.read_sql_query(f"""
        SELECT region_name || " " || ec.year AS region_and_year, ROUND(votes * 1.0 / voted * 100, 2) AS perc
        FROM 
            {elections}_elections_cand AS ec
            INNER JOIN {elections}_elections_region AS er ON ec.region_id = er.region_id AND ec.year = er.year
            INNER JOIN region USING(region_id)
        WHERE candidate_id = (
            SELECT candidate_id
            FROM {candidates}_candidate
            WHERE candidate_name = "{candidate}"
        ) AND ec.region_id <> (
            SELECT region_id
            FROM region
            WHERE region_name = "Вся Россия"
        )
        ORDER BY votes * 1.0 / voted DESC
        LIMIT 5
    """, connection)

    # Находим 5 худших результатов кандидата по всем регионам за все выборы
    data2 = pd.read_sql_query(f"""
        SELECT region_name || " " || ec.year AS region_and_year, ROUND(votes * 1.0 / voted * 100, 2) AS perc
        FROM 
            {elections}_elections_cand AS ec
            INNER JOIN {elections}_elections_region AS er ON ec.region_id = er.region_id AND ec.year = er.year
            INNER JOIN region USING(region_id)
        WHERE candidate_id = (
            SELECT candidate_id
            FROM {candidates}_candidate
            WHERE candidate_name = "{candidate}"
        ) AND ec.region_id <> (
            SELECT region_id
            FROM region
            WHERE region_name = "Вся Россия"
        )
        ORDER BY votes * 1.0 / voted
        LIMIT 5
    """, connection)

    # Находим 5 регионов, в которых кандидата любят больше всего
    data3 = pd.read_sql_query(f"""
        SELECT *
        FROM
        (
            SELECT candidate_id, ec.region_id, ROUND(SUM(votes * 1.0 / voted * 100) / COUNT(DISTINCT ec.year), 2) AS avg_perc
            FROM 
                {elections}_elections_cand AS ec
                INNER JOIN {elections}_elections_region AS er ON ec.region_id = er.region_id AND ec.year = er.year
            WHERE candidate_id = (
                SELECT candidate_id
                FROM {candidates}_candidate
                WHERE candidate_name = "{candidate}"
            )
            GROUP BY candidate_id, ec.region_id
            ORDER BY avg_perc DESC
            LIMIT 5
        ) region_ids 
        INNER JOIN region USING(region_id)
    """, connection)

    # Находим 5 регионов, в которых кандидата любят меньше всего
    data4 = pd.read_sql_query(f"""
        SELECT *
        FROM
        (
            SELECT candidate_id, ec.region_id, ROUND(SUM(votes * 1.0 / voted * 100) / COUNT(DISTINCT ec.year), 2) AS avg_perc
            FROM 
                {elections}_elections_cand AS ec
                INNER JOIN {elections}_elections_region AS er ON ec.region_id = er.region_id AND ec.year = er.year
            WHERE candidate_id = (
                SELECT candidate_id
                FROM {candidates}_candidate
                WHERE candidate_name = "{candidate}"
            )
            GROUP BY candidate_id, ec.region_id
            ORDER BY avg_perc
            LIMIT 5
        ) region_ids 
        INNER JOIN region USING(region_id)
    """, connection)

    go.Figure(layout={"template": "plotly"})

    # Строим столбчатую диаграмму для лучших результатов кандидата за все время
    fig1 = px.bar(data1, x="region_and_year", y="perc",
                  title="Лучшие результаты данного кандитата по регионам за все время",
                  custom_data=["region_and_year", "perc"],
                  labels={"region_and_year": "Регион и год", "perc": "Процент голосов"})
    # Немного обрезаем названия регионов, чтобы график не съезжал
    fig1.update_xaxes(
        labelalias={cand_year: cand_year[:-5][:15] + " " + cand_year[-4:]
                    for cand_year in data1["region_and_year"].values})
    # Настраиваем границы вертикальной оси таким образом, чтобы данные нормально отображались
    if data1["perc"].max() <= 5:
        fig1.update_yaxes(range=[0, 5])
    else:
        fig1.update_yaxes(range=[0, 10 * (data1["perc"].max() // 10 + 1)])
    # Настраиваем информацию, появляющуюся при наведении курсора на график
    fig1.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Процент голосов: %{customdata[1]}%<extra></extra>"
        ])
    )
    # Настраиваем цвет фона графика в соответствии с цветом страницы
    fig1.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    # Строим столбчатую диаграмму для худших результатов кандидата за все время
    fig2 = px.bar(data2, x="region_and_year", y="perc",
                  title="Худшие результаты данного кандидата по регионам за все время",
                  custom_data=["region_and_year", "perc"],
                  labels={"region_and_year": "Регион и год", "perc": "Процент голосов"})
    # Немного обрезаем названия регионов, чтобы график не съезжал
    fig2.update_xaxes(
        labelalias={cand_year: cand_year[:-5][:15] + " " + cand_year[-4:]
                    for cand_year in data2["region_and_year"].values})
    # Настраиваем границы вертикальной оси таким образом, чтобы данные нормально отображались
    if data2["perc"].max() <= 5:
        fig2.update_yaxes(range=[0, 5])
    else:
        fig2.update_yaxes(range=[0, 10 * (data2["perc"].max() // 10 + 1)])
    # Настраиваем информацию, появляющуюся при наведении курсора на график
    fig2.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Процент голосов: %{customdata[1]}%<extra></extra>"
        ])
    )
    # Настраиваем цвет фона графика в соответствии с цветом страницы
    fig2.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    # Строим столбчатую диаграмму для регионов, в которых кандидата любят больше всего
    fig3 = px.bar(data3, x="region_name", y="avg_perc",
                  title="Регионы, в которых кандидата любят больше всего",
                  custom_data=["region_name", "avg_perc"],
                  labels={"region_name": "Регион", "avg_perc": "Средний процент голосов за кандидата"})
    # Немного обрезаем названия регионов, чтобы график не съезжал
    fig3.update_xaxes(
        labelalias={reg: reg[:15] for reg in data3["region_name"].values})
    # Настраиваем границы вертикальной оси таким образом, чтобы данные нормально отображались
    if data3["avg_perc"].max() <= 5:
        fig3.update_yaxes(range=[0, 5])
    else:
        fig3.update_yaxes(range=[0, 10 * (data3["avg_perc"].max() // 10 + 1)])
    # Настраиваем информацию, появляющуюся при наведении курсора на график
    fig3.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Средний процент голосов в регионе: %{customdata[1]}%<extra></extra>"
        ])
    )
    # Настраиваем цвет фона графика в соответствии с цветом страницы
    fig3.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    # Строим столбчатую диаграмму для регионов, в которых кандидата любят меньше всего
    fig4 = px.bar(data4, x="region_name", y="avg_perc",
                  title="Регионы, в которых кандидата любят меньше всего",
                  custom_data=["region_name", "avg_perc"],
                  labels={"region_name": "Регион", "avg_perc": "Средний процент голосов за кандидата"})
    # Немного обрезаем названия регионов, чтобы график не съезжал
    fig4.update_xaxes(
        labelalias={reg: reg[:15] for reg in data4["region_name"].values})
    # Настраиваем границы вертикальной оси таким образом, чтобы данные нормально отображались
    if data4["avg_perc"].max() <= 5:
        fig4.update_yaxes(range=[0, 5])
    else:
        fig4.update_yaxes(range=[0, 10 * (data4["avg_perc"].max() // 10 + 1)])
    # Настраиваем информацию, появляющуюся при наведении курсора на график
    fig4.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Средний процент голосов в регионе: %{customdata[1]}%<extra></extra>"
        ])
    )
    # Настраиваем цвет фона графика в соответствии с цветом страницы
    fig4.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    return fig1, fig2, fig3, fig4


if __name__ == "__main__":
    app.run_server(debug=True)
