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
        dcc.Graph(id="total-sales-chart"),
        dcc.Graph(id="choropleth"),
    ],
)

@app.callback(
    Output("total-sales-chart", "figure"),
    [
        Input("customer_filter", "value"),
    ]
)
def make_sales_chart(customers):
    filters = {
        "customers": customers,
    }
    
    client.filter_dataframe(filters)
    figure = client.make_total_sales_chart()
    return figure

@app.callback(
    Output("choropleth", "figure"),
    [
        Input("customer_filter", "value")
    ]
)
def make_choropleth_chart(customers):
    filters = {
        "customers": customers,
    }

    client.filter_dataframe(filters)
    figure = client.make_choropleth_chart()
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
