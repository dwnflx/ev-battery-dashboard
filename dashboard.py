import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LinearRegression
from model import BatteryModel, Params, InitialValues
from BPTK_Py import sd_functions as sd

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

# Define a mapping between the display format and the dataset format
scenario_mapping = {
    'Stated Policies': 'Stated policies',
    'Announced Pledges': 'Announced pledges',
    'Net Zero 2050': 'Net zero 2050'
}

# Display the titleized options in the radio button widget
scenario_display = list(scenario_mapping.keys())  # Extract the keys as the display options
selected_scenario = st.sidebar.radio(
    "Scenario",
    scenario_display,
    index=0,  # Default is the first option
    help='Clean energy deployment trends under the Stated Policies Scenario (STEPS), Announced Pledges Scenario (APS) and Net Zero Emissions by 2050 Scenario (NZE) taken from the projections in the World Energy Outlook 2022, complemented by the results in the Energy Technology Perspectives 2023. \n\n The pace of mineral intensity improvements varies by scenario, with the STEPS generally seeing minimal improvement over time as compared to modest improvement (around 10% in the longer term) assumed in the APS.'
)

# Convert the selected display option back to its dataset format
scenario_actual = scenario_mapping[selected_scenario]

# Show selection
st.header(f"{st.session_state.selected_mineral} with a '{selected_scenario}' scenario")


# ==== Parameters ====
#st.sidebar.header('Parameters')


# Use st.markdown with custom CSS to adjust font size
def custom_text(text: str, font_size: str = "16px"):
    """Display text with custom font size using Markdown."""
    markdown = f"<p style='font-size: {font_size};'>{text}</p>"
    st.markdown(markdown, unsafe_allow_html=True)



# Create two columns for the parameters
col_battery, col_grid = st.sidebar.columns(2)

# Column for Battery parameters
with col_battery:
    st.header("Battery Parameters")  # Optional: Add a sub-header or text
    # EV Battery Recycling Rate
    battery_recycling_rate = st.slider(
        "EV Battery Recycling Rate",
        min_value=0.0, max_value=0.1, value=0.01, step=0.01
    )

    # EV Battery Repurpose Rate
    battery_repurpose_rate = st.slider(
        "EV Battery Repurpose Rate",
        min_value=0.0, max_value=0.1, value=0.01, step=0.01
    )

    # EV Battery Waste Rate
    battery_waste_rate = st.slider(
        "EV Battery Waste Rate",
        min_value=0.0, max_value=0.1, value=0.01, step=0.01
    )

# Column for Grid parameters
with col_grid:
    st.header("Grid Parameters")  # Optional: Add a sub-header or text
    # Grid Storage Recycling Rate
    grid_recycling_rate = st.slider(
        "Grid Storage Recycling Rate",
        min_value=0.0, max_value=0.1, value=0.01, step=0.01
    )

    # Grid Storage Waste Rate
    grid_waste_rate = st.slider(
        "Grid Storage Waste Rate",
        min_value=0.0, max_value=0.1, value=0.01, step=0.01
    )


    # Define the mapping of scenarios and minerals to their max reserve percentages
    max_values = {
        'Stated Policies': {
            'Nickel': 0.35,
            'Cobalt': 0.40,
            'Lithium': 0.75
        },
        'Announced Pledges': {
            'Nickel': 0.50,
            'Cobalt': 0.55,
            'Lithium': 0.85
        },
        'Net Zero 2050': {
            'Nickel': 0.50,
            'Cobalt': 0.55,
            'Lithium': 0.85
        }
    }
    
    # Retrieve the max_value for the current selections
    current_max_value = max_values[selected_scenario][st.session_state.selected_mineral]

    mat_max = {
        "Lithium": {
            "resources": 26000.0
        },
        "Nickel": {
            "resources": 100000.0
        },
        "Cobalt": {
            "resources": 8300.0
        }
    }

    # Mining value - annual amount of mineral mined (in kt)
    mining = st.slider(
        "Mining value",
        min_value=0.0, max_value=mat_max[st.session_state.selected_mineral]["resources"]*0.02, value=0.0, step=mat_max[st.session_state.selected_mineral]["resources"]*0.02/100,
        help="Annual amount of mineral mined (in kt)"
    )


if battery_waste_rate < 0:
    # Display an error message and stop loading the dashboard
    st.error("Invalid rates selected. Please ensure the combined recycling and repurpose rates do not exceed 100%.")
    
else:

   
    # ==== Demand vs Supply ====
    # Load the CSV data for mineral demand
    df = pd.read_csv('data/minerals_demand_long.csv')

    # Filter the data based on the scenario and mineral
    df_filtered = df[(df['scenario'] == scenario_actual) & (df['mineral'] == st.session_state.selected_mineral)]

    # Group by 'year' and sum the 'demand' to represent supply (and calculate demand)
    yearly_data = df_filtered.groupby('year')['demand'].sum().reset_index()

    # Extract the list of years from yearly_data
    years_in_yearly_data = yearly_data['year'].unique()

    # Calculate battery production
    demand_2025 = yearly_data.loc[yearly_data['year'] == 2025, 'demand'].values[0]
    demand_2022 = yearly_data.loc[yearly_data['year'] == 2022, 'demand'].values[0]
    battery_production = df_filtered.loc[:, 'demand'].mean()

    """
    params = Params(
        battery_recycling_rate,
        battery_repurpose_rate,
        battery_waste_rate,
        grid_recycling_rate,
        grid_waste_rate,
        extraction_limit,
        battery_production
    )
    """

    params = Params(
        mining=mining,
        battery_production=battery_production,
        battery_recycling_rate=battery_recycling_rate,
        battery_repurpose_rate=battery_repurpose_rate,
        battery_waste_rate=battery_waste_rate,
        grid_recycling_rate=grid_recycling_rate,
        grid_waste_rate=grid_waste_rate
    )

    init_values_dict = {
        "Lithium": {
            "resources": 26000.0,
            "stocks": 260.0,
            "batteries": 89.0,
            "grid": 300.0,
            "waste": 500.0
        },
        "Nickel": {
            "resources": 100000.0,
            "stocks": 1000.0,
            "batteries": 399.0,
            "grid": 1200.0,
            "waste": 300.0
        },
        "Cobalt": {
            "resources": 8300.0,
            "stocks": 80.0,
            "batteries": 133.0,
            "grid": 1000.0,
            "waste": 200.0
        }
    }


    mineral_values = InitialValues(**init_values_dict[st.session_state.selected_mineral])
    
    model = BatteryModel(params, mineral_values)
    df_stocks = model.get_stocks_df()

    # Filter df_stocks to include only rows where the 'year' is in years_in_yearly_data
    filtered_df_stocks = df_stocks[df_stocks.index.isin(years_in_yearly_data)].reset_index().rename(columns={'index': 'year'})

    yearly_data['supply'] = filtered_df_stocks['batteries']
    #st.dataframe(yearly_data.head())


    # Create a Plotly Express figure
    fig = px.line(filtered_df_stocks, x='year', y=[col for col in filtered_df_stocks.columns if col not in ['year', 'resources']], title='Stock Values Over Time')

    # Display the figure in Streamlit
    st.plotly_chart(fig)

    st.dataframe(filtered_df_stocks)
    
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
