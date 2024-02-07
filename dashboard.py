import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LinearRegression

st.set_page_config(layout="wide")

st.title('🔋 EV Battery Demand and Supply')

# SIDEBAR
# ==== Minerals ==== 
st.sidebar.header('Select Minerals')
# Create a row with three columns
col1, col2, col3 = st.sidebar.columns(3)
# Initialize a variable to hold the selected mineral
selected_mineral = None

# Using buttons to select minerals
if col1.button('Lithium'):
    selected_mineral = 'Lithium'
if col2.button('Cobalt'):
    selected_mineral = 'Cobalt'
if col3.button('Nickel'):
    selected_mineral = 'Nickel'


# ==== Parameters ====
st.sidebar.header('Parameters')
# Recycling percentage
recycling_rate = st.sidebar.slider('Recycling Rate (%)', min_value=0, max_value=100, value=50)
# Annual increase in EV production
annual_increase = st.sidebar.slider('Annual Increase in EV Production (%)', min_value=0, max_value=20, value=7)
# Efficiency improvements
efficiency_improvements = st.sidebar.slider('Efficiency Improvements (%)', min_value=0, max_value=10, value=2)


# ==== Demand vs Supply ====
# Sample data
data = pd.DataFrame({
    'Year': [2020, 2021, 2022, 2023, 2024],
    'Mineral_Demand': [100, 150, 200, 250, 300],
    'Mineral_Supply': [80, 130, 180, 230, 280]
})

# Creating the bar chart using Plotly
fig = go.Figure()
fig.add_trace(go.Bar(x=data['Year'], y=data['Mineral_Demand'], name='Demand', marker_color='#0e9c57'))
fig.add_trace(go.Bar(x=data['Year'], y=data['Mineral_Supply'], name='Supply', marker_color='#acc2a6'))
# Update layout for a more integrated look
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    font_color="#333333",  # Adjust font color to match the dashboard theme
    title="Yearly Mineral Demand vs. Supply",
    xaxis_title="Year",
    yaxis_title="Quantity",
    legend_title="Legend",
    barmode='group'
)

# Remove white lines and make it more integrated
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='rgba(0,0,0,0)')
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='rgba(0,0,0,0)')

# ==== Global Resource Map ====
# Sample data for the global map (replace with your actual data)
data_map = {
    'Country': ['United States', 'Australia', 'China', 'Brazil', 'Canada'],
    'Production': [1000, 1500, 2000, 1200, 800],
    'Latitude': [37.0902, -25.2744, 35.8617, -14.2350, 56.1304],
    'Longitude': [-95.7129, 133.7751, 104.1954, -51.9253, -106.3468]
}
df_map = pd.DataFrame(data_map)

# Creating the global production map (replace this with your map code)
fig_map = px.scatter_geo(df_map, lat='Latitude', lon='Longitude', size='Production', hover_name='Country', projection='natural earth', title='Global Production of Critical Minerals', color_discrete_sequence=["green"])
fig_map.update_layout(
    title={
        'text': "World Map regarding production",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    geo=dict(
        bgcolor='rgba(0,0,0,0)',  # Optional: Transparent background
        lakecolor='LightBlue',  # Optional: Color of the lakes
        landcolor='rgba(235, 235, 235, 0.5)',  # Optional: Light land color for integration
    ),
    paper_bgcolor='rgba(0,0,0,0)',  # Optional: Transparent background outside the map
    margin=dict(l=0, r=0, t=40, b=0)  # Adjust margins to make room for the title
)

# Use Streamlit columns to layout the bar chart and map side by side
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.plotly_chart(fig_map, use_container_width=True)



# ==== Forecasting EV Battery Demand ====
# Simple synthetic data for demonstration
years_demand = np.arange(2020, 2030)
demand_values = np.random.rand(10) * 100 + years_demand * 50  # Increasing trend

# Fit a simple linear regression model for forecasting
model_demand = LinearRegression().fit(years_demand.reshape(-1, 1), demand_values)

# Forecast for the next 5 years
future_years_demand = np.arange(2030, 2035)
forecast_demand = model_demand.predict(future_years_demand.reshape(-1, 1))

# Plotting the forecast
fig_forecast = go.Figure()
fig_forecast.add_trace(go.Scatter(x=years_demand, y=demand_values, mode='lines+markers', name='Actual Demand', marker_color='green', line=dict(color='forestgreen')))
fig_forecast.add_trace(go.Scatter(x=future_years_demand, y=forecast_demand, mode='lines+markers', name='Forecasted Demand', line=dict(color='limegreen', dash='dash')))
fig_forecast.update_layout(
    title='Forecasting EV Battery Demand',
    xaxis_title='Year',
    yaxis_title='Demand',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color="#333333"
)

# ==== Resource Depletion Timeline ====
# Resource Depletion Plot
current_reserves = 50000  # Example reserve quantity, adjust as per your data
annual_consumption = 2500  # Starting consumption
consumption_growth_rate = 0.05  # Annual growth in consumption

years = [2020]  # Starting year
reserves = [current_reserves]  # Starting reserves

year = 2020
while current_reserves > 0:
    year += 1
    annual_consumption *= (1 + consumption_growth_rate)
    current_reserves -= annual_consumption
    years.append(year)
    reserves.append(max(current_reserves, 0))  # Prevent negative reserves

# Create a depletion plot
fig_depletion = go.Figure()
fig_depletion.add_trace(go.Scatter(x=years, y=reserves, fill='tozeroy', mode='lines+markers', name='Remaining Reserves',line=dict(color='seagreen')))
fig_depletion.update_layout(
    title='Resource Depletion Timeline',
    xaxis_title='Year',
    yaxis_title='Remaining Reserves',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color="#333333"
)

# Display the new row of plots
col3, col4 = st.columns(2)

with col3:
    st.plotly_chart(fig_forecast, use_container_width=True)

with col4:
    st.plotly_chart(fig_depletion, use_container_width=True)
