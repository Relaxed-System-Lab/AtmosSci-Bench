import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question77(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Physical Oceanography"
        self.template = """Compare the dry-adiabatic lapse rate on {planet_name} with that of Earth given that the gravitational acceleration on {planet_name} is {g_planet} m/s^2 and its atmosphere is composed almost entirely of hydrogen and therefore has a different value of c_p."""
        self.func = self.calculate_lapse_rate_ratio
        self.default_variables = {
            "planet_name": "Jupiter",  # Default planet name
            "g_earth": 9.81,          # Gravitational acceleration on Earth (m/s^2)
            "g_planet": 26.0,         # Gravitational acceleration on Jupiter (m/s^2)
            "cp_earth": 1005.0,       # Specific heat capacity at constant pressure for Earth's atmosphere (J/kg/K)
            "cp_planet": 14e3         # Specific heat capacity at constant pressure for Jupiter's atmosphere (J/kg/K)
        }

        self.constant = {}
        
        self.independent_variables = {
            "g_earth": {"min": 9.0, "max": 10.0, "granularity": 0.01},
            "cp_earth": {"min": 900.0, "max": 1100.0, "granularity": 1.0},
        }
        
        self.dependent_variables = {}
        
        self.choice_variables = {
            "planet": [
                {"planet_name": "Mercury", "g_planet": 3.7, "cp_planet": 820.0},
                {"planet_name": "Venus", "g_planet": 8.87, "cp_planet": 920.0},
                {"planet_name": "Earth", "g_planet": 9.81, "cp_planet": 1005.0},
                {"planet_name": "Jupiter", "g_planet": 26.0, "cp_planet": 14e3},
            ]
        }
        
        self.custom_constraints = [
            lambda vars, res: vars["g_planet"] > vars["g_earth"],  # Ensure the chosen planet's gravity is greater than Earth's if default is Jupiter
            lambda vars, res: vars["cp_planet"] > vars["cp_earth"]  # Ensure the chosen planet's c_p is greater than Earth's if default is Jupiter
        ]

        super(Question77, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_lapse_rate_ratio(g_earth, g_planet, cp_earth, cp_planet, planet_name):
        """
        Calculate the ratio of dry-adiabatic lapse rates between Earth and another planet.

        Parameters:
        g_earth (float): Gravitational acceleration on Earth (m/s^2).
        g_planet (float): Gravitational acceleration on the chosen planet (m/s^2).
        cp_earth (float): Specific heat capacity at constant pressure for Earth's atmosphere (J/kg/K).
        cp_planet (float): Specific heat capacity at constant pressure for the chosen planet's atmosphere (J/kg/K).

        Returns:
        float: The ratio of dry-adiabatic lapse rates (Planet/Earth).
        """
        lapse_rate_ratio = (g_planet / g_earth) * (cp_earth / cp_planet)
        return Answer(lapse_rate_ratio, "", 3)


if __name__ == '__main__':
    q = Question77(unique_id="q")
    print(q.question())
    print(q.answer())