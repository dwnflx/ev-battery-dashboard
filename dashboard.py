import streamlit as st
import pandas as pd
import plotly.express as px
from model import BatteryModel, Params, InitialValues

st.set_page_config(layout="wide")

st.title('🔋 Mineral Resources for EV Batteries ♻️')


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
max_minerals = {
    "Lithium": 26000,
    "Nickel": 100000,
    "Cobalt": 8300
}
max_mineral = max_minerals[st.session_state.selected_mineral]

mining = st.sidebar.slider(
    "Mining value",
    min_value=0,
    max_value=max_mineral // 25,
    value=0,
    step=max_mineral // 5000,
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

    # EV Battery End of Life Rate
    battery_eol_rate = st.slider(
        "End of Life Rate",
        key="battery_eol_rate",
        min_value=0.0,
        max_value=10.0,
        value=1.0,
        step=0.5,
        format="%g%%",
        help="Annual percentage of batteries that reach their end of life and are no longer usable in EVs. They will be "
             "recycled, repurposed for use in grid storage, or go to waste."
    )

    # EV Battery Recycling Rate
    battery_recycling_rate = st.slider(
        "Recycling Rate",
        key="battery_recycling_rate",
        min_value=0.0,
        max_value=50.0,
        value=0.0,
        step=1.0,
        format="%g%%"
    )

    # EV Battery Repurpose Rate
    battery_repurpose_rate = st.slider(
        "Repurpose Rate",
        key="battery_repurpose_rate",
        min_value=0.0,
        max_value=50.0,
        value=0.0,
        step=1.0,
        format="%g%%"
    )


# Column for Grid parameters
with col_grid:
    st.subheader("Grid Storage")  # Optional: Add a sub-header or text

    # Grid Storage End of Life Rate
    grid_eol_rate = st.slider(
        "End of Life Rate",
        key="grid_eol_rate",
        min_value=0.0,
        max_value=10.0,
        value=1.0,
        step=0.5,
        format="%g%%",
        help="Annual percentage of batteries that reach their end of life and are no longer usable for grid storage. "
             "They will be recycled or go to waste."
    )

    # Grid Storage Recycling Rate
    grid_recycling_rate = st.slider(
        "Recycling Rate",
        key="grid_recycling_rate",
        min_value=0.0,
        max_value=50.0,
        value=0.0,
        step=1.0,
        format="%g%%"
    )

    # Define the mapping of scenarios and minerals to their max reserve percentages, e.g what share of the reserve can be allocated for battery production
    mineral_allocations = {
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
    mineral_allocation = mineral_allocations[selected_scenario][st.session_state.selected_mineral]


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

# Calculate battery production (mean demand)
battery_production = df_filtered.loc[:, 'demand'].mean()

# Different new finds rates for each mineral
new_finds_rates = {
    "Lithium": 0.07,
    "Nickel": 0.02,
    "Cobalt": 0.01
}
new_finds_rate = new_finds_rates[st.session_state.selected_mineral]

params = Params(
    mining=mining,
    battery_production=battery_production,
    battery_eol_rate=battery_eol_rate / 100.0,
    battery_recycling_rate=battery_recycling_rate / 100.0,
    battery_repurpose_rate=battery_repurpose_rate / 100.0,
    grid_eol_rate=grid_eol_rate / 100.0,
    grid_recycling_rate=grid_recycling_rate / 100.0,
    new_finds_rate=new_finds_rate / 100.0
)

# Initialize values per mineral - adapt with help of 'mineral_allocation' to reflect the true share depending on scenario/mineral chosen
init_values_dict = {
    "Lithium": {
        "resources": 26000.0 * mineral_allocation,
        "stocks": 260.0,
        "batteries": 89.0,
        "grid": 300.0,
        "waste": 500.0
    },
    "Nickel": {
        "resources": 100000.0 * mineral_allocation,
        "stocks": 1000.0,
        "batteries": 399.0,
        "grid": 1200.0,
        "waste": 300.0
    },
    "Cobalt": {
        "resources": 8300.0 * mineral_allocation,
        "stocks": 80.0,
        "batteries": 133.0,
        "grid": 1000.0,
        "waste": 200.0
    }
}

mineral_values = InitialValues(**init_values_dict[st.session_state.selected_mineral])

# Load model with corresponding parameters
model = BatteryModel(params, mineral_values)
df_stocks = model.get_stocks_df().reset_index(names='year')

st.write(f'Yearly demand (battery production): {battery_production:.2f} kt')

# Create a Plotly Express figure for both
col1, col2 = st.columns(2)
with col1:
    fig = px.line(df_stocks, x='year',
                  y=[col for col in df_stocks.columns if col not in ['year', 'resources']],
                  range_y=[-max_mineral // 8, max_mineral // 3],
                  title='Stock Values Over Time')
    fig.update_layout(legend_title_text='Variable')
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.line(df_stocks, x='year', y='resources',
                  range_y=[-max_mineral // 8, max_mineral * 2],
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
