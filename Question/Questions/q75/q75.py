import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question75(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Geophysics"
        self.template = """
Given that the acceleration due to gravity decays with height from the centre of the Earth following an inverse square law, what is the percentage change in g from the Earth's surface to an altitude of {altitude} km?
        """
        self.func = self.calculate_percentage_change_in_g
        self.default_variables = {
            "altitude": 100e3     # Altitude in meters (100 km)
        }

        self.constant = {
            "earth_radius": 6e6,  # Earth's radius in meters (6,000 km)
        }

        self.independent_variables = {
           # "earth_radius": {"min": 6e6, "max": 7e6, "granularity": 1e4},  # Earth's radius in meters
            "altitude": {"min": 1e3, "max": 500e3, "granularity": 1e3}    # Altitude in meters
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["altitude"] > 0,  # Altitude must be positive
          #  lambda vars, res: vars["earth_radius"] > vars["altitude"]  # Radius must be greater than altitude
        ]


        super(Question75, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_percentage_change_in_g(earth_radius, altitude):
        """
        Calculate the percentage change in gravitational acceleration (g) 
        from the Earth's surface to a given altitude.

        Parameters:
            earth_radius (float): Radius of the Earth in meters.
            altitude (float): Altitude above the Earth's surface in meters.

        Returns:
            float: Percentage change in g.
        """
        delta_r = altitude
        percentage_change = -2 * (delta_r / earth_radius) * 100
        return Answer(percentage_change, "%", 3)


if __name__ == '__main__':
    q = Question75(unique_id="q")
    print(q.question())
    print(q.answer())