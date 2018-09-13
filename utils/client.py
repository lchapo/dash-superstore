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
		self.years = sorted(self.unfiltered_df["Year"].unique())
		self.categories = sorted(self.unfiltered_df["Category"].unique())

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

	def _get_totals_by_subcategory(self, df):
	    # helper function to make scatter plot
	    data = []
	    for category in self.categories:
	        grouped = df.copy().loc[df["Category"] == category].groupby("Sub-Category")["Sales","Profit"].sum()
	        data.append({
	            'x': grouped.Sales.values,
	            'y': grouped.Profit.values,
	            'mode':'markers',
	            'text': grouped.index,
	            'name': category,
	        })
	    return data

	def make_scatterplot(self):
		# scatterplot showing sales vs profits, animated over time
		# show by subcategory and color by category

		frames = []

		for year in self.years:
		    dff = self.filtered_df.copy().loc[self.filtered_df["Year"] == year]
		    
		    frames.append(
		        {
		            'name': str(year),
		            'data': self._get_totals_by_subcategory(dff),
		        }
		    )

		duration = 1000

		steps = []
		for year in self.years:
		    steps.append(
		        {'args': [[year],
		        {'frame': {'duration': duration, 'redraw': False},
		         'mode': 'immediate',
		         'transition': {'duration': duration}}],
		       'label': str(year),
		       'method': 'animate'}
		    )

		sliders = [{'active': 0,
		    'yanchor': 'top',
		    'xanchor': 'left',
		    'currentvalue': {
		        'font': {'size': 20},
		        'prefix': 'Year:',
		        'visible': True,
		        'xanchor': 'right'
		    },
		    'transition': {
		        'duration': duration,
		        'easing': 'cubic-in-out'
		    },
		    'pad': {
		        'b': 10,
		        't': 50
		    },
		    'len': 0.9,
		    'x': .05,
		    'y': 0,
		    'steps': steps
		}]

		ymax = self.filtered_df.groupby(["Year","Sub-Category"])["Profit"].sum().max()
		ymin = self.filtered_df.groupby(["Year","Sub-Category"])["Profit"].sum().min()
		xmax = self.filtered_df.groupby(["Year","Sub-Category"])["Sales"].sum().max()

		layout = {
		    'xaxis': {
		        'title': 'Sales',
		        'range': [0, xmax * 1.15]
		    },
		    'yaxis': {
		        'title': 'Profit',
		        'range': [ymin - ymax * .15, ymax * 1.15],
		    },
		    'hovermode': 'closest',
		    'sliders': sliders,
		}

		figure = {
		    'data': frames[0]['data'],
		    'layout': layout,
		    'frames': frames,
		}

		return figure
