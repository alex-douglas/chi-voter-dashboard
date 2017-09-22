# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import geopandas as gpd
from shapely.geometry.multipolygon import MultiPolygon

# initailize Dash instance
app = dash.Dash()

# pull in boiler-plate CSS
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# test shape to confirm if trace shapes are MultiPolygons or Polygons
test_type = MultiPolygon()

# RGB values for darkest color on map
RED   = 48
GREEN = 63
BLUE  = 159

# .shp file column titles can only be 10 characters long,
# so we need a dictionary to map dropdown selection values to their column headers in the GeoDataFrame
column_dict = {'African American Race %': 'African Am',
				 'Bachelors or Higher %': 'Bachelors',
				 'Ballots Cast': 'Ballots Ca',
				 'Bikability Score': 'Bikability',
				 'Caucasian Race %': 'Caucasian',
				 'Crimes Past Month': 'Crimes P_1',
				 'Crimes Past Week': 'Crimes P_2',
				 'Crimes Past Year': 'Crimes Pas',
				 'Detached Housing %': 'Detached H',
				 'High School Graduation Rate': 'High Schoo',
				 'Hispanic Race %': 'Hispanic R',
				 'Median Age': 'Median Age',
				 'Median Income': 'Median Inc',
				 'Median Rent': 'Median Ren',
				 'Non-Citizen %': 'Non-Citize',
				 'Population Below Poverty Line %': 'Populati_2',
				 'Population Disabled %': 'Populati_1',
				 'Population Speaking English %': 'Population',
				 'Population With Income Over 100K %': 'Populati_3',
				 'Registerd Voters': 'Registerd',
				 'Total Population': 'Total Popu',
				 'Vacant Housing %': 'Vacant Hou',
				 'Voter Turnout': 'Voter Turn',
				 'Walkability Score': 'Walkabilit',
				 'Workers Traveling by Car Alone %': 'Workers Tr',
				 'Workers Traveling by Car Carpool %': 'Workers _1',
				 'Workers Traveling by Foot %': 'Workers _3',
				 'Workers Traveling by Public Transportation %': 'Workers _2'}

# read in our main dataFrame
df = gpd.read_file('/Users/adouglas/Google Drive/Metis/projects/passion_project/dash_df.shp')

# get our feature list for the dropdowns
available_features = list(column_dict.keys())

# return max value of metric, for color bar
def get_max_value(curr_metric, is_percent):
	if is_percent:
		max_val = max(df[curr_metric])*100
		if max_val < 10:
			return str(max_val)[:3] + '%'
		else:
			return str(max_val)[:4] + '%'
	else:
		return "{:,.0f}".format(max(df[curr_metric]))

# return min value of metric, for color bar
def get_min_value(curr_metric, is_percent):
	if is_percent:
		min_val = min(df[curr_metric])*100
		if min_val < 10:
			return str(min_val)[:3] + '%'
		else:
			return str(min_val)[:4] + '%'
	else:
		return "{:,.0f}".format(min(df[curr_metric]))

# get color for fill of each precinct shape, based on precinct metric value
def get_color(curr_metric, metric_val):
	max_val = max(df[curr_metric])
	min_val = min(df[curr_metric])

	cur_val = (metric_val - min_val) / (max_val - min_val)

	curr_red = int(255 - (cur_val * (255 - RED)))
	curr_green = int(255 - (cur_val * (255 - GREEN)))
	curr_blue = int(255 - (cur_val * (255 - BLUE)))
	color_val = 'rgba(' + str(curr_red) + ',' + str(curr_green) + ',' + str(curr_blue) + ',255)'
	
	return color_val

# main HTML layout of the dashboard
app.layout = html.Div(children=[html.H1(children='Features of Voter Turnout'),

	# left dropdown
	html.Div([
		dcc.Dropdown(
			id='avail-features-1',
			options=[{'label': i, 'value': i} for i in available_features],
			value='Population Below Poverty Line %'
		)
	],
	style={'width': '600', 'display': 'inline-block'}),

	# right dropdown
	html.Div([
		dcc.Dropdown(
			id='avail-features-2',
			options=[{'label': i, 'value': i} for i in available_features],
			value='Voter Turnout'
		)
	],
	style={'width': '600', 'display': 'inline-block', 'float': 'right', 'margin-right': '5'}),

	# correlation text
	html.Div(children=[html.H3(id='correlation-text', style={'text-align': 'center'})]),

	# left colorbar
	html.Div(id='color-bar-1',
			 children=[html.Div(id='min_val_1', style={'margin': '5', 'display': 'inline'}),
		 			   html.Div(style={'width': '500', 'height': '20', 'margin': '5', 'vertical-align': 'middle', 'display': 'inline-block', 'background': 'linear-gradient(90deg, white, #303F9F)'}),
		 			   html.P(id='max_val_1', style={'margin': '5', 'display': 'inline'})],
		 	 style={'display': 'inline-block'}),

	# right colorbar
	html.Div(id='color-bar-2',
			 children=[html.Div(id='min_val_2', style={'margin': '5', 'display': 'inline'}),
		 			   html.Div(style={'width': '500', 'height': '20', 'margin': '5', 'vertical-align': 'middle', 'display': 'inline-block', 'background': 'linear-gradient(90deg, white, #303F9F)'}),
		 			   html.P(id='max_val_2', style={'margin': '5', 'display': 'inline'})],
		 	 style={'display': 'inline-block', 'float': 'right'}),

	# left graph
	html.Div([
		dcc.Graph(
		id='graph-1'
		)
	], style={'display': 'inline-block'}),

	# right graph
	html.Div([
		dcc.Graph(
		id='graph-2'
		)
	], style={'float': 'right', 'display': 'inline-block'})
])

@app.callback(
	dash.dependencies.Output('min_val_1', 'children'),
	[dash.dependencies.Input('avail-features-1', 'value')])
def update_min_1(selected_feature):
	is_percent = False
	if '%' in selected_feature or selected_feature == 'Voter Turnout' or selected_feature == 'High School Graduation Rate':
		is_percent = True
	return get_min_value(column_dict[selected_feature], is_percent)

@app.callback(
	dash.dependencies.Output('max_val_1', 'children'),
	[dash.dependencies.Input('avail-features-1', 'value')])
def update_max_1(selected_feature):
	is_percent = False
	if '%' in selected_feature or selected_feature == 'Voter Turnout' or selected_feature == 'High School Graduation Rate':
		is_percent = True
	return get_max_value(column_dict[selected_feature], is_percent)

@app.callback(
	dash.dependencies.Output('min_val_2', 'children'),
	[dash.dependencies.Input('avail-features-2', 'value')])
def update_min_2(selected_feature):
	is_percent = False
	if '%' in selected_feature or selected_feature == 'Voter Turnout' or selected_feature == 'High School Graduation Rate':
		is_percent = True
	return get_min_value(column_dict[selected_feature], is_percent)

@app.callback(
	dash.dependencies.Output('max_val_2', 'children'),
	[dash.dependencies.Input('avail-features-2', 'value')])
def update_max_2(selected_feature):
	is_percent = False
	if '%' in selected_feature or selected_feature == 'Voter Turnout' or selected_feature == 'High School Graduation Rate':
		is_percent = True
	return get_max_value(column_dict[selected_feature], is_percent)

@app.callback(
	dash.dependencies.Output('correlation-text', 'children'),
	[dash.dependencies.Input('avail-features-1', 'value'),
	 dash.dependencies.Input('avail-features-2', 'value')])
def update_correlation(selected_feature_1, selected_feature_2):
	correlation = df[column_dict[selected_feature_1]].corr(df[column_dict[selected_feature_2]]) * 100

	if abs(correlation) < 10:
		if correlation > 0:
			return 'Correlation between ' + selected_feature_1 + ' and ' + selected_feature_2 + ': ' + str(correlation)[:3] + '%'
		else:
			return 'Correlation between ' + selected_feature_1 + ' and ' + selected_feature_2 + ': ' + str(correlation)[:4] + '%'
	else:
		if correlation > 0:
			return 'Correlation between ' + selected_feature_1 + ' and ' + selected_feature_2 + ': ' + str(correlation)[:4] + '%'
		else:
			return 'Correlation between ' + selected_feature_1 + ' and ' + selected_feature_2 + ': ' + str(correlation)[:5] + '%'


@app.callback(
	dash.dependencies.Output('graph-1', 'figure'),
	[dash.dependencies.Input('avail-features-1', 'value')])
def update_graph_1(selected_feature):

	traces = []

	for index, row in df.iterrows():
		if type(row.geometry) == type(test_type):
			for polygon in row.geometry:
				x, y = polygon.exterior.coords.xy

				trace = dict(type = 'scatter',
					 showlegend = False,
					 line = dict(width=0.5,color='rgba(13,13,13,255)'),
	        		 x = x,
	        		 y = y,
	        		 fill = 'toself',
	        		 fillcolor = get_color(column_dict[selected_feature], row[column_dict[selected_feature]])
	        		 )

				traces.append(trace)
		else:
			x, y = row['geometry'].exterior.coords.xy

			trace = dict(type = 'scatter',
						 showlegend = False,
						 line = dict(width=0.5,color='rgba(13,13,13,255)'),
		        		 x = x,
		        		 y = y,
		        		 fill = 'toself',
		        		 fillcolor = get_color(column_dict[selected_feature], row[column_dict[selected_feature]])
		        		 )

			traces.append(trace)

	return {
		'data': traces,
		'layout': go.Layout(title=selected_feature,
							autosize=False,
							width='600',
							height='600',
							yaxis=dict(autorange=True,
							           showgrid=False,
							           zeroline=False,
							           showline=False,
							           autotick=True,
							           ticks='',
							           showticklabels=False),
							xaxis=dict(autorange=True,
							           showgrid=False,
							           zeroline=False,
							           showline=False,
							           autotick=True,
							           ticks='',
							           showticklabels=False)
							)
	}

@app.callback(
	dash.dependencies.Output('graph-2', 'figure'),
	[dash.dependencies.Input('avail-features-2', 'value')])
def update_graph_2(selected_feature):

	traces = []

	for index, row in df.iterrows():
		if type(row.geometry) == type(test_type):
			for polygon in row.geometry:
				x, y = polygon.exterior.coords.xy

				trace = dict(type = 'scatter',
					 showlegend = False,
					 line = dict(width=0.5,color='rgba(13,13,13,255)'),
	        		 x = x,
	        		 y = y,
	        		 fill = 'toself',
	        		 fillcolor = get_color(column_dict[selected_feature], row[column_dict[selected_feature]])
	        		 )

				traces.append(trace)
		else:
			x, y = row['geometry'].exterior.coords.xy

			trace = dict(type = 'scatter',
						 showlegend = False,
						 line = dict(width=0.5,color='rgba(13,13,13,255)'),
		        		 x = x,
		        		 y = y,
		        		 fill = 'toself',
		        		 fillcolor = get_color(column_dict[selected_feature], row[column_dict[selected_feature]])
		        		 )

			traces.append(trace)

	return {
		'data': traces,
		'layout': go.Layout(title=selected_feature,
							autosize=False,
							width='600',
							height='600',
							yaxis=dict(autorange=True,
							           showgrid=False,
							           zeroline=False,
							           showline=False,
							           autotick=True,
							           ticks='',
							           showticklabels=False),
							xaxis=dict(autorange=True,
							           showgrid=False,
							           zeroline=False,
							           showline=False,
							           autotick=True,
							           ticks='',
							           showticklabels=False)
							)
	}

if __name__ == '__main__':
	app.run_server()
