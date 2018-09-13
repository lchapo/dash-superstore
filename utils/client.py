"""  Backend client handling data functions
"""

import json

import numpy as np
import pandas as pd

scl = [[0.0, 'rgb(242,240,247)'],[0.2, 'rgb(218,218,235)'],[0.4, 'rgb(188,189,220)'],\
            [0.6, 'rgb(158,154,200)'],[0.8, 'rgb(117,107,177)'],[1.0, 'rgb(84,39,143)']]

class Client(object):
	def __init__(self, filters=None):
		self.filters = filters
		self.unfiltered_df = self._load_data()
		self.filtered_df = self.unfiltered_df.copy()
		self.unique_customers = self.unfiltered_df["Customer Name"].unique()

	def _load_data(self):
		# load data from xlsx file and add calculated cols
		df = pd.read_excel("data/Superstore Data.xlsx")
		
		# get 2-letter state abbreviations
		with open('data/states.json') as json_file:
			state_mapping = json.load(json_file)
		df["State Code"] = df["State"].map(state_mapping)

		# get year
		df["Year"] = df["Order Date"].apply(lambda x: x.year)

		return df

	def filter_dataframe(self, filters):
		self.filters = filters
		df = self.unfiltered_df.copy()

		if not self.filters["customers"]:
			customer_bool = np.ones(len(df),dtype=bool)
		else:
			# convert unicode to strings
			customers = [str(i) for i in self.filters["customers"]]
			customer_bool = (df["Customer Name"].isin(customers)) 

		filters = customer_bool
		dff = df.loc[filters].reset_index(drop=True)
		self.filtered_df = dff

	def make_total_sales_chart(self):
		# show total sales by category

		grouped = self.filtered_df.groupby("Category").sum()
		traces = [
    		dict(
    			type="bar",
    			x=grouped.index.values,
    			y=grouped["Sales"].values,
    		)
    	]

		layout = [
			dict(
				title="Total Sales by Category"
			)
		]

		figure = dict(data=traces, layout=layout)
		return figure

	def make_choropleth_chart(self):
		# heatmap by state
		df = self.filtered_df.copy().groupby("State Code").sum()

		df["text"] = df.index \
		    + "<br>" + "Sales: " + df["Sales"].astype(str) \
		    + "<br>" + "Profit: " + df["Profit"].astype(str)

		data = [ dict(
		    type='choropleth',
		    colorscale = scl,
		    autocolorscale = False,
		    locations = df.index,
		    z = df['Sales'].astype(float),
		    locationmode = 'USA-states',
		    hoverinfo="text",
		    text = df['text'],
		    marker = dict(
		        line = dict (
		            color = 'rgb(255,255,255)',
		            width = 2
		        ) ),
		    colorbar = dict(
		        title = "Total Sales")
		) ]

		layout = dict(
		    title = 'State Heatmap by Total Sales (Hover for Profit)',
		    geo = dict(
		        scope='usa',
		        projection=dict( type='albers usa' ),
		        showlakes = True,
		        lakecolor = 'rgb(255, 255, 255)'),
		)

		figure = dict(data=data, layout=layout)
		return figure

	def make_scatter(self):
		# scatterplot showing sales vs profits, animated over time
		# show by subcategory and color by category

		years = sorted(self.unfiltered_df["Year"].unique())

		figure = {
		    'data': [],
		    'layout': {},
		    'frames': []
		}

		figure['layout']['xaxis'] = {'title': 'Sales'}
		figure['layout']['yaxis'] = {'title': 'Profit'}
		figure['layout']['hovermode'] = 'closest'
		
		figure['layout']['sliders'] = {
		    'args': [
		        'transition', {
		            'duration': 400,
		            'easing': 'cubic-in-out'
		        }
		    ],
		    'initialValue': years[0],
		    'plotlycommand': 'animate',
		    'values': years,
		    'visible': True
		}

		figure['layout']['updatemenus'] = [
		    {
		        'buttons': [
		            {
		                'args': [None, {'frame': {'duration': 500, 'redraw': False},
		                         'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
		                'label': 'Play',
		                'method': 'animate'
		            },
		            {
		                'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
		                'transition': {'duration': 0}}],
		                'label': 'Pause',
		                'method': 'animate'
		            }
		        ],
		        'direction': 'left',
		        'pad': {'r': 10, 't': 87},
		        'showactive': False,
		        'type': 'buttons',
		        'x': 0.1,
		        'xanchor': 'right',
		        'y': 0,
		        'yanchor': 'top'
		    }
		]

		sliders_dict = {
		    'active': 0,
		    'yanchor': 'top',
		    'xanchor': 'left',
		    'currentvalue': {
		        'font': {'size': 20},
		        'prefix': 'Year:',
		        'visible': True,
		        'xanchor': 'right'
		    },
		    'transition': {'duration': 300, 'easing': 'cubic-in-out'},
		    'pad': {'b': 10, 't': 50},
		    'len': 0.9,
		    'x': 0.1,
		    'y': 0,
		    'steps': []
		}

		# make list of categories
		categories = self.filtered_df["Category"].unique()

		# make data
		year = years[0]
		for category in categories:
		    dataset_by_year = dataset[dataset['year'] == year]
		    dataset_by_year_and_cont = dataset_by_year[dataset_by_year['continent'] == continent]

		    data_dict = {
		        'x': list(dataset_by_year_and_cont['lifeExp']),
		        'y': list(dataset_by_year_and_cont['gdpPercap']),
		        'mode': 'markers',
		        'text': list(dataset_by_year_and_cont['country']),
		        'marker': {
		            'sizemode': 'area',
		            'sizeref': 200000,
		            'size': list(dataset_by_year_and_cont['pop'])
		        },
		        'name': continent
		    }
		    figure['data'].append(data_dict)
		    
		# make frames
		for year in years:
		    frame = {'data': [], 'name': str(year)}
		    for continent in continents:
		        dataset_by_year = dataset[dataset['year'] == int(year)]
		        dataset_by_year_and_cont = dataset_by_year[dataset_by_year['continent'] == continent]

		        data_dict = {
		            'x': list(dataset_by_year_and_cont['lifeExp']),
		            'y': list(dataset_by_year_and_cont['gdpPercap']),
		            'mode': 'markers',
		            'text': list(dataset_by_year_and_cont['country']),
		            'marker': {
		                'sizemode': 'area',
		                'sizeref': 200000,
		                'size': list(dataset_by_year_and_cont['pop'])
		            },
		            'name': continent
		        }
		        frame['data'].append(data_dict)

		    figure['frames'].append(frame)
		    slider_step = {'args': [
		        [year],
		        {'frame': {'duration': 300, 'redraw': False},
		         'mode': 'immediate',
		       'transition': {'duration': 300}}
		     ],
		     'label': year,
		     'method': 'animate'}
		    sliders_dict['steps'].append(slider_step)

		figure['layout']['sliders'] = [sliders_dict]

		return figure
