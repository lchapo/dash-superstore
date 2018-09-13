# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html

from utils.client import Client

client = Client()
app = dash.Dash()

# html
app.layout = html.Div(
    [
        html.H1("Superstore Metrics"),
        dcc.Dropdown(
            id="customer_filter",
            options=[{
                "label": i,
                "value": i,
            } for i in client.unique_customers],
            value=[],
            multi=True,
            placeholder="All Customers",
        ),
        html.H1("Range Slider"),
        html.Div(
            [
                dcc.RangeSlider(
                    id="year_filter",
                    min=client.years[0],
                    max=client.years[-1],
                    value=[client.years[0], client.years[-1]],
                    step=1,
                    allowCross=False,
                    marks={year:str(year) for year in client.years},
                )
            ],
            style={'height': '50px', 'padding-top': '20px', 'padding-bottom': '20px', 'display': 'block'},
        ),
        dcc.Graph(id="total-sales-chart"),
        dcc.Graph(id="choropleth"),
        dcc.Graph(id="scatterplot"),
        dcc.Graph(id="piechart"),
    ],
)

@app.callback(
    Output("total-sales-chart", "figure"),
    [
        Input("customer_filter", "value"),
        Input("year_filter", "value"),
    ]
)
def make_sales_chart(customers, years):
    filters = {
        "customers": customers,
        "years": years,
    }
    
    client.filter_dataframe(filters)
    figure = client.make_total_sales_chart()
    return figure

@app.callback(
    Output("choropleth", "figure"),
    [
        Input("customer_filter", "value"),
        Input("year_filter", "value"),
    ]
)
def make_choropleth_chart(customers, years):
    filters = {
        "customers": customers,
        "years": years,
    }

    client.filter_dataframe(filters)
    figure = client.make_choropleth_chart()
    return figure

@app.callback(
    Output("scatterplot", "figure"),
    [
        Input("customer_filter", "value"),
        Input("year_filter", "value"),
    ]
)
def make_scatterplot(customers, years):
    filters = {
        "customers": customers,
        "years": years,
    }

    client.filter_dataframe(filters)
    figure = client.make_scatterplot()
    return figure

@app.callback(
    Output("piechart", "figure"),
    [
        Input("customer_filter", "value"),
        Input("year_filter", "value"),
    ]
)
def make_piechart(customers, years):
    filters = {
        "customers": customers,
        "years": years,
    }

    client.filter_dataframe(filters)
    figure = client.make_piechart()
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
