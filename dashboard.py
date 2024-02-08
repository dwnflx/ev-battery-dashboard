import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LinearRegression

st.set_page_config(layout="wide")


st.title('🔋 EV Battery - simulation with recycling ♻️')

# Rate of new findings for mineral sources per year
NEW_FINDS = 0.05

# SIDEBAR
# ==== Minerals and Scenario ==== 
st.sidebar.header('Select Mineral and Scenario')
# Create a row with three columns
col1, col2, col3 = st.sidebar.columns(3)
# Initialize session_state for selected_mineral if it doesn't exist
if 'selected_mineral' not in st.session_state:
    st.session_state.selected_mineral = 'Lithium'

# Using buttons to select minerals
if col1.button('Lithium'):
    st.session_state.selected_mineral = 'Lithium'
if col2.button('Cobalt'):
    st.session_state.selected_mineral = 'Cobalt'
if col3.button('Nickel'):
    st.session_state.selected_mineral = 'Nickel'

# Scenario Selection
scenario = st.sidebar.radio(
    "Scenario",
    ['Stated policies', 'Announced pledges', 'Net zero 2050'],
    index=0  # Default is 'Stated policies'
)

# Show selection
st.header(f"{st.session_state.selected_mineral} with a '{scenario}' scenario")

# ==== Parameters ====
st.sidebar.header('Battery parameters')
# Sidebar - EV Battery Recycling Rate
battery_recycling_rate = st.sidebar.slider(
    "EV Battery Recycling Rate",
    min_value=0.0, max_value=1.0, value=0.3, step=0.1
)

# Sidebar - EV Battery Repurpose Rate
battery_repurpose_rate = st.sidebar.slider(
    "EV Battery Repurpose Rate",
    min_value=0.0, max_value=1.0, value=0.3, step=0.1
)

# Sidebar - EV Battery Waste Rate
battery_waste_rate = round(1 - battery_recycling_rate - battery_repurpose_rate, 2) / 100
st.sidebar.write(f"EV Battery Waste Rate: {battery_waste_rate * 100:.2f}%")


# Sidebar - EV Battery Lifespan
battery_lifespan = st.sidebar.slider(
    "EV Battery Lifespan",
    min_value=5, max_value=20, value=10, step=1
)

st.sidebar.header('Grid parameters')
# Sidebar - Grid Storage Recycling Rate
grid_recycling_rate = st.sidebar.slider(
    "Grid Storage Recycling Rate",
    min_value=0.0, max_value=1.0, value=0.3, step=0.1
)

# Sidebar - Grid Storage Waste Rate
grid_waste_rate = round(1 - grid_recycling_rate, 2) / 100
st.sidebar.write(f"Grid Waste Rate: {grid_waste_rate * 100:.2f}%")

# Sidebar - Grid Storage Lifecycle
grid_lifespan = st.sidebar.slider(
    "Grid Storage Lifecycle",
    min_value=5, max_value=20, value=10, step=1
)

# Sidebar - Extraction Limit Until 2050
extraction_limit = st.sidebar.slider(
    "Extraction Limit Until 2050",
    min_value=0.1, max_value=0.8, value=0.3, step=0.1
)

if battery_waste_rate < 0:
    # Display an error message and stop loading the dashboard
    st.error("Invalid rates selected. Please ensure the combined recycling and repurpose rates do not exceed 100%.")
    
else:
    # ==== Demand vs Supply ====
    # Load the CSV data for mineral demand
    df = pd.read_csv('data/minerals_demand_long.csv')
    
    # Filter the data based on the scenario and mineral
    df_filtered = df[(df['scenario'] == scenario) & (df['mineral'] == st.session_state.selected_mineral)]

    
    # Group by 'year' and sum the 'demand' to represent supply (and calculate demand)
    # SUPPLY AS FILLER FOR NOW
    yearly_data = df_filtered.groupby('year')['demand'].sum().reset_index()
    yearly_data['demand'] = yearly_data['demand']  # Assuming this is actually the supply
    yearly_data['supply'] = yearly_data['demand'] * 1.10  # Calculating demand as 1.10 times supply
    
    # Creating the bar chart using Plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(x=yearly_data['year'], y=yearly_data['demand'], name='Demand', marker_color='#0e9c57'))
    fig.add_trace(go.Bar(x=yearly_data['year'], y=yearly_data['supply'], name='Supply', marker_color='#acc2a6'))
    
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
    # Load the CSV file into a DataFrame
    df_reserves = pd.read_csv('data/Reserves_enriched.csv', sep=';', encoding='utf-8')

    # Filter the DataFrame for the selected mineral
    df_selected_mineral = df_reserves[df_reserves['Mineral'] == st.session_state.selected_mineral]
    
    # Creating the global reserves map
    fig_map = px.scatter_geo(df_selected_mineral, 
                             lat='Latitude', 
                             lon='Longitude', 
                             size='Reserves 2023 (in 1.000 Tons)', 
                             hover_name='Country', 
                             projection='natural earth', 
                             title=f'Global Reserves of {st.session_state.selected_mineral}', 
                             color_discrete_sequence=["green"])
    
    fig_map.update_layout(
        title={
            'text': f"World Map of {st.session_state.selected_mineral} Reserves (2023)",
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
