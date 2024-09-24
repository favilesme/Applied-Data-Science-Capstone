
# Import required libraries  
import pandas as pd  
import dash
from dash import html
from dash import dcc  
from dash.dependencies import Input, Output  
import plotly.express as px  

# Read the SpaceX launch data into a pandas DataFrame  
spacex_df = pd.read_csv("spacex_launch_dash.csv")  
max_payload = spacex_df['Payload Mass (kg)'].max()  
min_payload = spacex_df['Payload Mass (kg)'].min()  

# Create a Dash application  
app = dash.Dash(__name__)  

# Create the app layout  
app.layout = html.Div(children=[  
    html.H1('SpaceX Launch Records Dashboard',  
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),  
    
    # Dropdown for selecting the launch site  
    dcc.Dropdown(  
        id='site-dropdown',  
        options=[  
            {'label': 'All Sites', 'value': 'ALL'},  
            {'label': 'CCSFS', 'value': 'CCSFS'},  
            {'label': 'KSC', 'value': 'KSC'},  
            {'label': 'LC-40', 'value': 'LC-40'},  
            {'label': 'VAFB', 'value': 'VAFB'},  
        ],  
        value='ALL',  
        placeholder='Select a Launch Site here',  
        searchable=True  
    ),  
    
    html.Br(),  

    # Pie chart for launch success  
    html.Div(dcc.Graph(id='success-pie-chart')),  
    html.Br(),  

    html.P("Payload range (Kg):"),  

    # Slider for selecting payload range  
    dcc.RangeSlider(  
        id='payload-slider',  
        min=0,  
        max=10000,  
        step=1000,  
        value=[min_payload, max_payload],  
        marks={i: str(i) for i in range(0, 10001, 1000)}  
    ),  

    # Scatter chart for payload vs success  
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),  
])  

# Callback for the pie chart  
@app.callback(  
    Output(component_id='success-pie-chart', component_property='figure'),  
    Input(component_id='site-dropdown', component_property='value')  
)  
def get_pie_chart(entered_site):  
    filtered_df = spacex_df  
    
    if entered_site == 'ALL':  
        # Prepare pie chart data for all sites  
        success_counts = filtered_df.groupby('Launch Site')['class'].value_counts().unstack().fillna(0)  
        success_percentage = (success_counts[1] / (success_counts[0] + success_counts[1])) * 100  
        success_percentage = success_percentage.fillna(0)  # Fill NaN values with 0  
        fig = px.pie(  
            names=success_percentage.index,  
            values=success_percentage,  
            title='Launch Success Percentage for All Sites'  
        )  
    else:  
        # Prepare pie chart data for a specific site  
        filtered_site_df = filtered_df[filtered_df['Launch Site'] == entered_site]  
        success_counts = filtered_site_df['class'].value_counts()  
        success_percentage = success_counts / success_counts.sum() * 100  # Calculate percentages  
        fig = px.pie(  
            names=success_counts.index,  
            values=success_percentage,  
            title='Launch Success Percentage for {}'.format(entered_site)  
        )  

    return fig  

# Callback for the scatter plot  
@app.callback(  
    Output(component_id='success-payload-scatter-chart', component_property='figure'),  
    [Input(component_id='site-dropdown', component_property='value'),  
     Input(component_id="payload-slider", component_property="value")]  
)  
def update_scatter_chart(selected_site, payload_range):  
    # Filter based on payload range  
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &   
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]  

    if selected_site != 'ALL':  
        # Filter by selected site  
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]  

    scatter_fig = px.scatter(  
        filtered_df,  
        x='Payload Mass (kg)',  
        y='class',  
        color='Booster Version Category',  
        title='Payload vs. Launch Success for {} Launch Site'.format(selected_site if selected_site != 'ALL' else 'All Sites')  
    )  
    return scatter_fig  

# Run the app  
if __name__ == '__main__':  
    app.run_server(debug=True)