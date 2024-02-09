import pandas as pd
from BPTK_Py import Model
from BPTK_Py.sddsl import Stock

from dataclasses import dataclass

START_YEAR = 2022
END_YEAR = 2050
NEW_FINDS_PERCENT = 0.05


@dataclass
class Params:
    # Rates between 0 and 1
    battery_recycling_rate: float
    battery_repurpose_rate: float
    battery_waste_rate: float
    grid_recycling_rate: float
    grid_waste_rate: float
    extraction_limit: float

    # Mineral used in battery production in kt
    battery_production: float


# Initial values in kt
@dataclass
class InitialValues:
    resources: float
    stocks: float
    batteries: float
    grid: float
    waste: float


class BatteryModel():
    def __init__(self, params: Params, values: InitialValues):
        self.model = Model(starttime=START_YEAR, stoptime=END_YEAR, dt=1, name='EV battery model')

        # Stocks
        self.resources = self.model.stock("resources")
        self.stocks = self.model.stock("stocks")
        self.batteries = self.model.stock("batteries")
        self.grid = self.model.stock("grid")
        self.waste = self.model.stock("waste")

        # Flows
        self.battery_production = self.model.flow("battery_production")
        self.battery_recycling = self.model.flow("battery_recycling")
        self.battery_repurpose = self.model.flow("battery_repurpose")
        self.battery_waste = self.model.flow("battery_waste")
        self.grid_recycling = self.model.flow("grid_recycling")
        self.grid_waste = self.model.flow("grid_waste")

        # Constants
        self.new_finds = self.model.constant("new_finds")
        self.mining = self.model.constant("mining")

        self.battery_recycling_rate = self.model.constant("battery_recycling_rate")
        self.battery_repurpose_rate = self.model.constant("battery_repurpose_rate")
        self.battery_waste_rate = self.model.constant("battery_waste_rate")
        self.grid_recycling_rate = self.model.constant("grid_recycling_rate")
        self.grid_waste_rate = self.model.constant("grid_waste_rate")

        # Stock equations
        self.resources.equation = self.new_finds - self.mining
        self.stocks.equation = self.mining + self.battery_recycling + self.grid_recycling - self.battery_production
        self.batteries.equation = self.battery_production - self.battery_recycling - self.battery_repurpose - self.battery_waste
        self.grid.equation = self.battery_repurpose - self.grid_recycling - self.grid_waste
        self.waste.equation = self.battery_waste + self.grid_waste

        # Flow equations
        self.battery_production.equation = params.battery_production
        self.battery_recycling.equation = self.battery_recycling_rate * self.batteries
        self.battery_repurpose.equation = self.battery_repurpose_rate * self.batteries
        self.battery_waste.equation = self.battery_waste_rate * self.batteries
        self.grid_recycling_rate = self.grid_recycling_rate * self.grid
        self.grid_waste_rate = self.grid_waste_rate * self.grid

        # Initialization
        self.resources.initial_value = values.resources
        self.stocks.initial_value = values.stocks
        self.batteries.initial_value = values.batteries
        self.grid.initial_value = values.grid
        self.waste.initial_value = values.waste

        # Constant equations
        self.battery_recycling_rate.equation = params.battery_recycling_rate
        self.battery_repurpose_rate.equation = params.battery_repurpose_rate
        self.battery_waste_rate.equation = params.battery_waste_rate
        self.grid_recycling_rate.equation = params.grid_recycling_rate

        self.new_finds.equation = self.resources.initial_value * NEW_FINDS_PERCENT
        self.mining.equation = self.resources.initial_value * params.extraction_limit / (END_YEAR - START_YEAR)


    def get_stocks_df(self) -> pd.DataFrame:
        stocks = self._get_stocks()
        df = pd.concat([stock.plot(return_df=True) for stock in stocks.values()], axis=1)
        df.index = df.index.astype(int)
        return df

    def _get_stocks(self) -> dict[str, Stock]:
        return {
            "resources": self.resources,
            "stocks": self.stocks,
            "batteries": self.batteries,
            "grid": self.grid,
            "waste": self.waste
        }
