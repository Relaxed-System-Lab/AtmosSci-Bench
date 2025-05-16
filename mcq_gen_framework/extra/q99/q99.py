import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question99(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """Molten lava, characterized by a density of {density} kg/m^3 and a viscosity of {viscosity} Pa·s, travels through a conduit with a circular cross-sectional shape. The conduit has a diameter of {diameter} m, and the lava flow is motivated by a pressure gradient of {pressure_gradient} Pa/m. Given the assumption that the flow is laminar, determine the lava discharge in m^3/s. Is the laminar flow assumption appropriate?"""

        self.func = self.calculate_discharge_and_regime

        self.default_variables = {
            "density": 2700.0,               # kg/m^3
            "viscosity": 1.0e3,              # Pa·s
            "diameter": 1.0,                 # m
            "pressure_gradient": -2000.0     # Pa/m
        }

        self.constant = {}

        self.independent_variables = {
            "density": {"min": 1000, "max": 3500, "granularity": 10},
            "viscosity": {"min": 100, "max": 5000, "granularity": 10},
            "diameter": {"min": 0.1, "max": 5.0, "granularity": 0.01},
            "pressure_gradient": {"min": -10000, "max": -500, "granularity": 10}
        }

        self.dependent_variables = {
            # No explicit dependent variables; output is derived from all inputs
        }

        self.choice_variables = {
        }

        self.custom_constraints = [
            lambda vars, res: vars["pressure_gradient"] < 0,
            lambda vars, res: res["is_laminar"] == True  # flow is laminar
        ]

        super(Question99, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_discharge_and_regime(density, viscosity, diameter, pressure_gradient):
        """
        Calculate the volumetric discharge (m^3/s) and determine whether the lava flow is laminar.
        """
        radius = diameter / 2
        area = math.pi * radius**2
        avg_velocity = (-pressure_gradient) * (diameter**2) / (32 * viscosity)
        discharge = avg_velocity * area
        reynolds_number = (density * avg_velocity * diameter) / viscosity
        is_laminar = reynolds_number < 2000
        return NestedAnswer({
            "discharge": Answer(discharge, "m^3/s", 3),
            "is_laminar": Answer(is_laminar, "", None)
        })

if __name__ == '__main__':
    q = Question99(unique_id="q")
    print(q.question())
    print(q.answer())