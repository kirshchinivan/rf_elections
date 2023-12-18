from dash import html, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import dash
import json
import sqlite3

with open("russia.geojson", encoding="UTF-8") as response:
    counties = json.load(response)

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SLATE])
server = app.server

app.layout = html.Div([
    dash.page_container
])


@callback(
    [Output("map_dropdown", "options"),
     Output("map_dropdown", "value")],
    [Input("year_dropdown", "value"),
     Input("map_dropdown", "value")]
)
def update_options(year, param):
    connection = sqlite3.connect("elections.db")

    if year in [2003, 2007, 2011]:
        candidates = "gd"
        elections = "gd"
    else:
        candidates = "p"
        elections = "president"

    candidates = pd.read_sql_query(f"""
        SELECT candidate_name
        FROM (
            SELECT DISTINCT candidate_id
            FROM {elections}_elections_cand
            WHERE year = {year}
            ) cand_ids
            INNER JOIN {candidates}_candidate USING(candidate_id)
    """, connection)["candidate_name"].values

    options = ["Явка"] + [f"Голоса за {cand}" for cand in candidates]
    if param not in options:
        param = "Явка"

    return options, param


@callback(
    Output("map", "figure"),
    [Input("map_dropdown", "value"),
     Input("year_dropdown", "value"),
     Input("region_dropdown", "value")]
)
def update_graph(param, year, region):
    connection = sqlite3.connect("elections.db")

    if year in [2003, 2007, 2011]:
        candidates = "gd"
        elections = "gd"
    else:
        candidates = "p"
        elections = "president"

    if region == "Вся Россия":
        if param == "Явка":
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

            fig = px.choropleth_mapbox(data, geojson=counties, locations="region_id", color="turnout",
                                       color_continuous_scale="deep",
                                       range_color=(0, 100),
                                       mapbox_style="carto-positron",
                                       zoom=1.25, center={"lat": 70, "lon": 94},
                                       hover_data="region_name", custom_data=["region_name", "turnout"],
                                       labels={"turnout": "Явка"})
            fig.update_traces(
                hovertemplate="<br>".join([
                    "%{customdata[0]}",
                    "Явка: %{customdata[1]}%"
                ])
            )
        else:
            param = param[10:]

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

            fig = px.choropleth_mapbox(data, geojson=counties, locations="region_id", color="perc",
                                       color_continuous_scale="deep",
                                       range_color=(0, 100),
                                       mapbox_style="carto-positron",
                                       zoom=1.25, center={"lat": 70, "lon": 94},
                                       hover_data="region_name", custom_data=["region_name", "perc"],
                                       labels={"perc": f"Голоса"})
            fig.update_traces(
                hovertemplate="<br>".join([
                    "%{customdata[0]}",
                    "Процент голосов: %{customdata[1]}%"
                ])
            )
    else:
        data = pd.read_sql_query(f"""
            SELECT region_id, region_name, CASE WHEN region_name = "{region}" THEN 100 ELSE 0 END AS color
            FROM region
            """, connection)

        fig = px.choropleth_mapbox(data, geojson=counties, locations="region_id", color="color",
                                   color_continuous_scale="reds",
                                   range_color=(0, 100),
                                   mapbox_style="carto-positron",
                                   zoom=1.25, center={"lat": 70, "lon": 94},
                                   hover_data="region_name", custom_data=["region_name"])
        fig.update_traces(
            hovertemplate="%{customdata[0]}"
        )
        fig.update_layout(coloraxis_showscale=False)
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        height=550,
        coloraxis_colorbar={"ticksuffix": "%"}
    )

    return fig


@callback(
    [Output("region_dropdown", "value"),
     Output("reset", "n_clicks")],
    [Input("map", "clickData"),
     Input("reset", "n_clicks")]
)
def update_region(clickData, n_clicks):
    if clickData is None:
        return "Вся Россия", 0

    if n_clicks > 0:
        return "Вся Россия", 0

    return clickData["points"][0]["customdata"][0], 0


@callback(
    [Output("results", "figure"),
     Output("turnout", "figure")],
    [Input("region_dropdown", "value"),
     Input("year_dropdown", "value")]
)
def update_graph(region, year):
    connection = sqlite3.connect("elections.db")

    if year in [2003, 2007, 2011]:
        candidates = "gd"
        elections = "gd"
    else:
        candidates = "p"
        elections = "president"

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

    data2 = pd.read_sql_query(f"""
        SELECT voted, came - voted AS not_voted, voters - came AS not_came
        FROM {elections}_elections_region
        WHERE year = {year} AND region_id = (
            SELECT region_id
            FROM region
            WHERE region_name = "{region}"
            )
    """, connection)

    fig1 = px.pie(data1, values="votes", names="candidate_name",
                  title=f"Итоги голосования")
    fig1.update_traces(
        hovertemplate="<br>".join([
            "%{label}",
            "Количество голосов: %{value}"
        ])
    )
    fig1.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        height=300
    )

    fig2 = px.pie(values=[data2["voted"][0], data2["not_voted"][0], data2["not_came"][0]],
                  names=["Проголосовали", "Пришли, но не проголосовали", "Не пришли"],
                  title=f"Явка")
    fig2.update_traces(
        hovertemplate="<br>".join([
            "%{label}",
            "%{value}"
        ])
    )
    fig2.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        height=300
    )

    return fig1, fig2


@callback(
    [Output("turnout_best", "figure"),
     Output("turnout_worst", "figure")
     ],
    Input("year_dropdown_2", "value")
)
def update_graph(year):
    connection = sqlite3.connect("elections.db")

    if year in [2003, 2007, 2011]:
        elections = "gd"
    else:
        elections = "president"

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

    fig1 = px.bar(top5_turnout, x="region_name", y="turnout", color="color",
                  title="Лучшие по явке регионы в выбранный год", labels={"region_name": "Регион", "turnout": "Явка"},
                  custom_data=["region_name", "turnout"])
    fig1.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Явка: %{customdata[1]}%<extra></extra>"
        ])
    )
    fig1.update_xaxes(labelalias={reg: reg[:15] for reg in top5_turnout["region_name"].values})
    fig1.update_yaxes(range=[0, 100])
    fig1.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        showlegend=False
    )

    fig2 = px.bar(worst5_turnout, x="region_name", y="turnout", color="color",
                  title="Худшие по явке регионы в выбранный год",
                  labels={"region_name": "Регион", "turnout": "Явка"},
                  custom_data=["region_name", "turnout"])
    fig2.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Явка: %{customdata[1]}%<extra></extra>"
        ])
    )
    fig2.update_xaxes(labelalias={reg: reg[:15] for reg in worst5_turnout["region_name"].values})
    fig2.update_yaxes(range=[0, 100])
    fig2.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        showlegend=False
    )

    return fig1, fig2


@callback(
    [Output("cand_best", "figure"),
     Output("cand_worst", "figure")],
    Input("region_dropdown_2", "value")
)
def update_graph(region):
    connection = sqlite3.connect("elections.db")

    if region[-1] == " ":
        candidates = "gd"
        elections = "gd"
    else:
        candidates = "p"
        elections = "president"
    region = region.strip()

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

    fig1 = px.bar(data1, x="candidate_name", y="avg_perc",
                  title="Самые любимые кандидаты в данном регионе",
                  custom_data=["candidate_name", "avg_perc"],
                  labels={"candidate_name": "Кандидат", "avg_perc": "Средний процент голосов за кандидата"})
    fig1.update_xaxes(labelalias={cand: cand[:15] for cand in data1["candidate_name"].values})
    fig1.update_yaxes(range=[0, 100])
    fig1.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Средний процент голосов в регионе: %{customdata[1]}%<extra></extra>"
        ])
    )
    fig1.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    fig2 = px.bar(data2, x="candidate_name", y="avg_perc",
                  title="Самые нелюбимые кандидаты в данном регионе",
                  custom_data=["candidate_name", "avg_perc"],
                  labels={"candidate_name": "Кандидат", "avg_perc": "Средний процент голосов за кандидата"})
    fig2.update_xaxes(labelalias={cand: cand[:15] for cand in data2["candidate_name"].values})
    fig2.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Средний процент голосов в регионе: %{customdata[1]}%<extra></extra>"
        ])
    )
    fig2.update_yaxes(range=[0, 5])
    fig2.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    return fig1, fig2


@callback(
    [Output("cand_top5", "figure"),
     Output("cand_worst5", "figure"),
     Output("cand_top5_reg", "figure"),
     Output("cand_worst5_reg", "figure")],
    Input("candidate_dropdown", "value")
)
def update_graph(candidate):
    connection = sqlite3.connect("elections.db")

    if candidate in pd.read_sql_query("SELECT candidate_name FROM gd_candidate", connection)["candidate_name"].values:
        candidates = "gd"
        elections = "gd"
    else:
        candidates = "p"
        elections = "president"

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

    fig1 = px.bar(data1, x="region_and_year", y="perc",
                  title="Лучшие результаты данного кандитата по регионам за все время",
                  custom_data=["region_and_year", "perc"],
                  labels={"region_and_year": "Регион и год", "perc": "Процент голосов"})
    fig1.update_xaxes(
        labelalias={cand_year: cand_year[:-5][:15] + " " + cand_year[-4:]
                    for cand_year in data1["region_and_year"].values})
    if data1["perc"].max() <= 5:
        fig1.update_yaxes(range=[0, 5])
    else:
        fig1.update_yaxes(range=[0, 10 * (data1["perc"].max() // 10 + 1)])
    fig1.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Процент голосов: %{customdata[1]}%<extra></extra>"
        ])
    )
    fig1.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    fig2 = px.bar(data2, x="region_and_year", y="perc",
                  title="Худшие результаты данного кандидата по регионам за все время",
                  custom_data=["region_and_year", "perc"],
                  labels={"region_and_year": "Регион и год", "perc": "Процент голосов"})
    fig2.update_xaxes(
        labelalias={cand_year: cand_year[:-5][:15] + " " + cand_year[-4:]
                    for cand_year in data2["region_and_year"].values})
    if data2["perc"].max() <= 5:
        fig2.update_yaxes(range=[0, 5])
    else:
        fig2.update_yaxes(range=[0, 10 * (data2["perc"].max() // 10 + 1)])
    fig2.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Процент голосов: %{customdata[1]}%<extra></extra>"
        ])
    )
    fig2.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    fig3 = px.bar(data3, x="region_name", y="avg_perc",
                  title="Регионы, в которых кандидата любят больше всего",
                  custom_data=["region_name", "avg_perc"],
                  labels={"region_name": "Регион", "avg_perc": "Средний процент голосов за кандидата"})
    fig3.update_xaxes(
        labelalias={reg: reg[:15] for reg in data3["region_name"].values})
    if data3["avg_perc"].max() <= 5:
        fig3.update_yaxes(range=[0, 5])
    else:
        fig3.update_yaxes(range=[0, 10 * (data3["avg_perc"].max() // 10 + 1)])
    fig3.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Средний процент голосов в регионе: %{customdata[1]}%<extra></extra>"
        ])
    )
    fig3.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    fig4 = px.bar(data4, x="region_name", y="avg_perc",
                  title="Регионы, в которых кандидата любят меньше всего",
                  custom_data=["region_name", "avg_perc"],
                  labels={"region_name": "Регион", "avg_perc": "Средний процент голосов за кандидата"})
    fig4.update_xaxes(
        labelalias={reg: reg[:15] for reg in data4["region_name"].values})
    if data4["avg_perc"].max() <= 5:
        fig4.update_yaxes(range=[0, 5])
    else:
        fig4.update_yaxes(range=[0, 10 * (data4["avg_perc"].max() // 10 + 1)])
    fig4.update_traces(
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Средний процент голосов в регионе: %{customdata[1]}%<extra></extra>"
        ])
    )
    fig4.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    return fig1, fig2, fig3, fig4


if __name__ == "__main__":
    app.run_server(debug=True)
