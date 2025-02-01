import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question37(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Physical Oceanography"
        self.template = """
Assume that, in the mixed layer, mixing maintains a vertically uniform temperature. A heat flux of {heat_flux} W/m^2 is applied at the ocean surface. Taking a representative value for the mixed layer depth, determine how long it takes for the mixed layer to warm up by {temperature_change}°C.
[Use density of water = {water_density} kg/m^3; specific heat of water = {specific_heat} J/(kg·K).]
        """
        self.func = self.calculate_warming_time
        self.default_variables = {
            "heat_flux": 25.0,  # Heat flux at the surface in W/m^2
            "mixed_layer_depth": 100.0,  # Depth of the mixed layer in meters
            "temperature_change": 1.0,  # Desired temperature change in °C
        }

        self.constant = {
                "water_density": 1000.0,  # Density of water in kg/m^3}
                "specific_heat": 4187.0,  # Specific heat of water in J/(kg·K)
        }

        self.independent_variables = {
            "heat_flux": {"min": 10.0, "max": 50.0, "granularity": 0.1},
            "mixed_layer_depth": {"min": 10.0, "max": 200.0, "granularity": 1.0}
        }

        self.dependent_variables = {
            "temperature_change": lambda vars: 1.0  # Always warming by 1°C in this scenario
        }

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["heat_flux"] > 0,
            lambda vars, res: vars["mixed_layer_depth"] > 0,
        ]

    

        super(Question37, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_warming_time(heat_flux, mixed_layer_depth, water_density, specific_heat, temperature_change):
        """
        Calculate the time it takes for the ocean's mixed layer to warm up by a given temperature change.

        Parameters:
            heat_flux (float): Heat flux applied at the surface in W/m^2.
            mixed_layer_depth (float): Depth of the mixed layer in meters.
            water_density (float): Density of water in kg/m^3.
            specific_heat (float): Specific heat of water in J/(kg·K).
            temperature_change (float): Desired temperature change in K.

        Returns:
            float: Time taken to achieve the temperature change in seconds.
        """
        # Calculate the heat capacity per unit area of the mixed layer
        heat_capacity_per_unit_area = specific_heat * water_density * mixed_layer_depth

        # Calculate the warming rate (dT/dt)
        warming_rate = heat_flux / heat_capacity_per_unit_area

        # Calculate the time to achieve the temperature change
        warming_time = temperature_change / warming_rate

        # Convert time to years
        warming_year = warming_time / (60 * 60 * 24 * 365.25)
        return Answer(warming_year, "yr", 1)


if __name__ == '__main__':
    q = Question37(unique_id="q")
    print(q.question())
    print(q.answer())