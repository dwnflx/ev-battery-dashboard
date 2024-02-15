import streamlit as st
import pandas as pd
import plotly.express as px
from model import BatteryModel, Params, InitialValues

st.set_page_config(layout="wide")

st.title('🔋 EV Battery - simulation with recycling ♻️')


#####################
# ==== SIDEBAR ==== #
#####################

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
    help='Clean energy deployment trends under the Stated Policies Scenario (STEPS), Announced Pledges Scenario (APS) '
         'and Net Zero Emissions by 2050 Scenario (NZE) taken from the projections in the World Energy Outlook 2022, '
         'complemented by the results in the Energy Technology Perspectives 2023. \n\n The pace of mineral intensity '
         'improvements varies by scenario, with the STEPS generally seeing minimal improvement over time as compared '
         'to modest improvement (around 10% in the longer term) assumed in the APS.'
)

# Convert the selected display option back to its dataset format
scenario_actual = scenario_mapping[selected_scenario]

# Show selection
st.header(f"{st.session_state.selected_mineral} with a '{selected_scenario}' scenario")

# ==== Parameters ====

# Mining value - annual amount of mineral mined (in kt)
mat_max = {
    "Lithium": 26000,
    "Nickel": 100000,
    "Cobalt": 8300
}
mat_max_selected = mat_max[st.session_state.selected_mineral]

mining = st.sidebar.slider(
    "Mining value",
    min_value=0,
    max_value=mat_max_selected // 25,
    value=0,
    step=mat_max_selected // 5000,
    format="%gkt",
    help="Annual amount of mineral mined. Try to match the yearly demand of the selected mineral shown on the right. "
         "As you increase recycling and repurpose rates, less mining is required to keep mineral stocks for battery "
         "production above zero."
)

# Create two columns for the parameters
col_battery, col_grid = st.sidebar.columns(2)

# Column for Battery parameters
with col_battery:
    st.subheader("EV Battery")  # Optional: Add a sub-header or text
    # EV Battery Recycling Rate
    battery_recycling_rate_prct = st.slider(
        "Recycling Rate",
        key="battery_recycling_rate",
        min_value=0.0,  # This now represents 0%
        max_value=10.0,  # This now represents 10%
        value=0.0,  # Default value, representing 0%
        step=1.0,  # Step size, representing 1%
        format="%g%%"  # Display format, showing the value as a percentage
    )

    # Convert the slider value back to a fraction
    battery_recycling_rate = battery_recycling_rate_prct / 100.0

    # EV Battery Repurpose Rate
    battery_repurpose_rate_prct = st.slider(
        "Repurpose Rate",
        key="battery_repurpose_rate",
        min_value=0.0,  # This now represents 0%
        max_value=10.0,  # This now represents 10%
        value=0.0,  # Default value, representing 0%
        step=1.0,  # Step size, representing 1%
        format="%g%%"  # Display format, showing the value as a percentage
    )

    # Convert the slider value back to a fraction
    battery_repurpose_rate = battery_repurpose_rate_prct / 100.0

    # EV Battery Waste Rate
    battery_waste_rate_prct = st.slider(
        "Waste Rate",
        key="battery_waste_rate",
        min_value=0.0,  # This now represents 0%
        max_value=10.0,  # This now represents 10%
        value=0.0,  # Default value, representing 0%
        step=1.0,  # Step size, representing 1%
        format="%g%%"  # Display format, showing the value as a percentage
    )

    # Convert the slider value back to a fraction
    battery_waste_rate = battery_waste_rate_prct / 100.0

# Column for Grid parameters
with col_grid:
    st.subheader("Grid Storage")  # Optional: Add a sub-header or text
    # Grid Storage Recycling Rate
    grid_recycling_rate_prct = st.slider(
        "Recycling Rate",
        key="grid_recycling_rate",
        min_value=0.0,  # This now represents 0%
        max_value=10.0,  # This now represents 10%
        value=0.0,  # Default value, representing 0%
        step=1.0,  # Step size, representing 1%
        format="%g%%"  # Display format, showing the value as a percentage
    )

    # Convert the slider value back to a fraction
    grid_recycling_rate = grid_recycling_rate_prct / 100.0

    # Grid Storage Waste Rate
    grid_waste_rate_prct = st.slider(
        "Waste Rate",
        key="grid_waste_rate",
        min_value=0.0,  # This now represents 0%
        max_value=10.0,  # This now represents 10%
        value=0.0,  # Default value, representing 0%
        step=1.0,  # Step size, representing 1%
        format="%g%%"  # Display format, showing the value as a percentage
    )

    # Convert the slider value back to a fraction
    grid_waste_rate = grid_waste_rate_prct / 100.0

    # Define the mapping of scenarios and minerals to their max reserve percentages, e.g what share of the reserve can be allocated for battery production
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


#######################
# ==== DASHBOARD ==== #
#######################

# ==== Stock Values and Resources Over Time ====
# Load the CSV data for mineral demand
df = pd.read_csv('data/minerals_demand_long.csv')

# Filter the data based on the scenario and mineral
df_filtered = df[((df['scenario'] == scenario_actual) |
                  ((df['year'] == 2022) & (df['scenario'] == 'Baseline'))) &
                 (df['mineral'] == st.session_state.selected_mineral)]

# Group by 'year' and sum the 'demand' to represent supply (and calculate demand)
yearly_data = df_filtered.groupby('year')['demand'].sum().reset_index()

# Extract the list of years from yearly_data
years_in_yearly_data = yearly_data['year'].unique()

# Calculate battery production
demand_2025 = yearly_data.loc[yearly_data['year'] == 2025, 'demand'].values[0]
demand_2022 = yearly_data.loc[yearly_data['year'] == 2022, 'demand'].values[0]
battery_production = df_filtered.loc[:, 'demand'].mean()

params = Params(
    mining=mining,
    battery_production=battery_production,
    battery_recycling_rate=battery_recycling_rate,
    battery_repurpose_rate=battery_repurpose_rate,
    battery_waste_rate=battery_waste_rate,
    grid_recycling_rate=grid_recycling_rate,
    grid_waste_rate=grid_waste_rate
)

# Initialize values per mineral - adapt with help of 'current_max_value' to reflect the true share depending on scenario/mineral chosen
init_values_dict = {
    "Lithium": {
        "resources": 26000.0 * current_max_value,
        "stocks": 260.0,
        "batteries": 89.0,
        "grid": 300.0,
        "waste": 500.0
    },
    "Nickel": {
        "resources": 100000.0 * current_max_value,
        "stocks": 1000.0,
        "batteries": 399.0,
        "grid": 1200.0,
        "waste": 300.0
    },
    "Cobalt": {
        "resources": 8300.0 * current_max_value,
        "stocks": 80.0,
        "batteries": 133.0,
        "grid": 1000.0,
        "waste": 200.0
    }
}

mineral_values = InitialValues(**init_values_dict[st.session_state.selected_mineral])

# Load model with corresponding parameters
model = BatteryModel(params, mineral_values)
df_stocks = model.get_stocks_df()

# Filter df_stocks to include only rows where the 'year' is in years_in_yearly_data
filtered_df_stocks = df_stocks[df_stocks.index.isin(years_in_yearly_data)].reset_index().rename(columns={'index': 'year'})

yearly_data['supply'] = filtered_df_stocks['batteries']

# st.dataframe(filtered_df_stocks)
st.write(f'Yearly demand (battery production): {battery_production:.2f} kt')

# Create a Plotly Express figure for both
col1, col2 = st.columns(2)
with col1:
    fig = px.line(filtered_df_stocks, x='year',
                  y=[col for col in filtered_df_stocks.columns if col not in ['year', 'resources']],
                  range_y=[-mat_max_selected // 8, mat_max_selected // 3],
                  title='Stock Values Over Time')
    fig.update_layout(legend_title_text='Variable')
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.line(filtered_df_stocks, x='year', y='resources',
                  range_y=[-mat_max_selected // 8, mat_max_selected],
                  title='Resources Over Time')
    st.plotly_chart(fig, use_container_width=True)


# ==== Global Resource Map ====
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
        'y': 0.9,
        'x': 0.5,
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

st.plotly_chart(fig_map, use_container_width=True)
