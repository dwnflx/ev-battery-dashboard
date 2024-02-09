from BPTK_Py import Model
from BPTK_Py.sddsl import Stock


class BatteryModel():
    def __init__(self):
        self.model = Model(starttime=2022, stoptime=2050, dt=1, name='EV battery model')

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
        # self.battery_lifespan = self.model.constant("battery_lifespan")
        # self.grid_lifespan = self.model.constant("grid_lifespan")
        # self.extraction_limit  = self.model.constant("extraction_limit")

        # Stock equations
        self.resources.equation = self.new_finds - self.mining
        self.stocks.equation = self.mining + self.battery_recycling + self.grid_recycling - self.battery_production
        self.batteries.equation = self.battery_production - self.battery_recycling - self.battery_repurpose - self.battery_waste
        self.grid.equation = self.battery_repurpose - self.grid_recycling - self.grid_waste
        self.waste.equation = self.battery_waste + self.grid_waste

        # Flow equations
        self.battery_recycling.equation = self.battery_recycling_rate * self.batteries
        self.battery_repurpose.equation = self.battery_repurpose_rate * self.batteries
        self.battery_waste.equation = self.battery_waste_rate * self.batteries
        self.grid_recycling_rate = self.grid_recycling_rate * self.grid
        self.grid_waste_rate = self.grid_waste_rate * self.grid

        # Initialization
        self.battery_recycling_rate.equation = 0.05
        self.battery_repurpose_rate.equation = 0.02
        self.battery_waste_rate.equation = 0.03  # 1 - battery_recycling_rate - battery_repurpose_rate
        self.grid_recycling_rate.equation = 0.05

        self.new_finds.equation = 1000
        self.mining.equation = 3000
        self.battery_production.equation = 4000

        self.resources.initial_value = 100000.0
        self.stocks.initial_value = 100.0
        self.batteries.initial_value = 1000.0
        self.grid.initial_value = 300.0
        self.waste.initial_value = 500.0

    def get_stocks(self) -> dict[str, Stock]:
        return {
            "resources": self.resources,
            "stocks": self.stocks,
            "batteries": self.batteries,
            "grid": self.grid,
            "waste": self.waste
        }
