import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question24(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
Suppose that the relative vorticity at the top of an Ekman layer at {latitude} is {vorticity} s^-1. Let the eddy viscosity coefficient be {eddy_viscosity} m^2/s, and the water vapor mixing ratio at the top of the Ekman layer be {water_mixing_ratio} g/kg. Estimate the precipitation rate owing to moisture convergence in the Ekman layer.
        """
        self.func = self.calculate_precipitation_rate
        self.default_variables = {
            "latitude": "15°N",
            "vorticity": 2e-5,          # s^-1
            "eddy_viscosity": 10,       # m^2/s
            "coriolis_param": 3.77e-5,  # s^-1 (Coriolis parameter at 15 degrees N)
            "water_mixing_ratio": 12    # g/kg
        }
        self.independent_variables = {
            "vorticity": {"min": 1e-6, "max": 1e-4, "granularity": 1e-6},
            "eddy_viscosity": {"min": 1, "max": 20, "granularity": 1},
            "water_mixing_ratio": {"min": 1, "max": 20, "granularity": 0.1}
        }
        self.dependent_variables = {}
        self.choice_variables = {
            "latitude": [
                {"latitude": "15°N", "coriolis_param": 3.77e-5},
                {"latitude": "30°N", "coriolis_param": 7.29e-5},
                {"latitude": "45°N", "coriolis_param": 1.03e-4}
            ]
        }
        self.custom_constraints = []

        super(Question24, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_precipitation_rate(vorticity, eddy_viscosity, coriolis_param, water_mixing_ratio, latitude):
        """
        Calculate the precipitation rate owing to moisture convergence in the Ekman layer.

        Returns:
            Precipitation rate in mm/day.
        """
        air_density = 1.1  # Air density (kg/m^3), default value from the problem
        water_density = 1000  # Water density (kg/m^3), default value for liquid water

        # Convert water vapor mixing ratio from g/kg to kg/kg
        water_mixing_ratio_kg = water_mixing_ratio / 1000

        # Calculate the vertical velocity scale (w_De)
        vertical_velocity_scale = math.sqrt(eddy_viscosity / (2 * coriolis_param))

        # Calculate precipitation rate (P) in kg/m^2/s
        precipitation_rate_kg_per_s = (
            air_density * water_mixing_ratio_kg * vorticity * vertical_velocity_scale
        )

        # Convert to mm/day
        precipitation_rate_mm_per_day = (
            precipitation_rate_kg_per_s / water_density * 1000 * 86400
        )

        return Answer(precipitation_rate_mm_per_day, "mm/day", 1)



if __name__ == '__main__':
    q = Question24(unique_id="q")
    print(q.question())
    print(q.answer())