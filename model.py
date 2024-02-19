import pandas as pd
from BPTK_Py import Model
from BPTK_Py.sddsl import Stock

from dataclasses import dataclass

START_YEAR = 2022
END_YEAR = 2050


@dataclass
class Params:
    # Mineral use in kt
    battery_production: float
    mining: float

    # Rates between 0 and 1
    battery_eol_rate: float
    battery_recycling_rate: float
    battery_repurpose_rate: float
    grid_eol_rate: float
    grid_recycling_rate: float
    new_finds_rate: float


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
        self.new_finds = self.model.flow("new_finds")
        self.mining = self.model.flow("mining")
        self.battery_production = self.model.flow("battery_production")
        self.battery_recycling = self.model.flow("battery_recycling")
        self.battery_repurpose = self.model.flow("battery_repurpose")
        self.battery_waste = self.model.flow("battery_waste")
        self.grid_recycling = self.model.flow("grid_recycling")
        self.grid_waste = self.model.flow("grid_waste")

        # Constants
        self.battery_recycling_rate = self.model.constant("battery_recycling_rate")
        self.battery_repurpose_rate = self.model.constant("battery_repurpose_rate")
        self.battery_waste_rate = self.model.constant("battery_waste_rate")
        self.grid_recycling_rate = self.model.constant("grid_recycling_rate")
        self.grid_waste_rate = self.model.constant("grid_waste_rate")
        self.new_finds_rate = self.model.constant("new_finds_rate")

        # Stock equations
        self.resources.equation = self.new_finds - self.mining
        self.stocks.equation = self.mining + self.battery_recycling + self.grid_recycling - self.battery_production
        self.batteries.equation = self.battery_production - self.battery_recycling - self.battery_repurpose - self.battery_waste
        self.grid.equation = self.battery_repurpose - self.grid_recycling - self.grid_waste
        self.waste.equation = self.battery_waste + self.grid_waste

        # Initialization
        self.resources.initial_value = values.resources
        self.stocks.initial_value = values.stocks
        self.batteries.initial_value = values.batteries
        self.grid.initial_value = values.grid
        self.waste.initial_value = values.waste

        # Flow equations
        self.new_finds.equation = self.resources.initial_value * params.new_finds_rate
        self.mining.equation = params.mining
        self.battery_production.equation = params.battery_production
        self.battery_recycling.equation = self.battery_recycling_rate * params.battery_eol_rate * self.batteries
        self.battery_repurpose.equation = self.battery_repurpose_rate * params.battery_eol_rate * self.batteries
        self.battery_waste.equation = self.battery_waste_rate * params.battery_eol_rate * self.batteries
        self.grid_recycling.equation = self.grid_recycling_rate * params.grid_eol_rate * self.grid
        self.grid_waste.equation = self.grid_waste_rate * params.grid_eol_rate * self.grid

        # Constant equations
        self.battery_recycling_rate.equation = params.battery_recycling_rate
        self.battery_repurpose_rate.equation = params.battery_repurpose_rate
        self.battery_waste_rate.equation = 1 - params.battery_recycling_rate - params.battery_repurpose_rate
        self.grid_recycling_rate.equation = params.grid_recycling_rate
        self.grid_waste_rate.equation = 1 - params.grid_recycling_rate
        self.new_finds_rate.equation = params.new_finds_rate

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
