import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question77(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
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
                {"planet_name": "Mars", "g_planet": 3.71, "cp_planet": 850.0},
                {"planet_name": "Jupiter", "g_planet": 26.0, "cp_planet": 14000.0},
                {"planet_name": "Saturn", "g_planet": 10.44, "cp_planet": 12500.0},
                {"planet_name": "Uranus", "g_planet": 8.87, "cp_planet": 10000.0},
                {"planet_name": "Neptune", "g_planet": 11.15, "cp_planet": 9500.0},
                {"planet_name": "Pluto", "g_planet": 0.62, "cp_planet": 600.0},
                {"planet_name": "Europa", "g_planet": 1.31, "cp_planet": 720.0},
                {"planet_name": "Ganymede", "g_planet": 1.43, "cp_planet": 850.0},
                {"planet_name": "Io", "g_planet": 1.79, "cp_planet": 880.0},
                {"planet_name": "Callisto", "g_planet": 1.24, "cp_planet": 730.0},
                {"planet_name": "Titan", "g_planet": 1.35, "cp_planet": 750.0},
                {"planet_name": "Triton", "g_planet": 0.78, "cp_planet": 650.0},
                {"planet_name": "Moon", "g_planet": 1.62, "cp_planet": 770.0},
                {"planet_name": "Ceres", "g_planet": 0.27, "cp_planet": 580.0},
                {"planet_name": "Eris", "g_planet": 0.82, "cp_planet": 700.0},
                {"planet_name": "Haumea", "g_planet": 0.44, "cp_planet": 620.0},
                {"planet_name": "Makemake", "g_planet": 0.50, "cp_planet": 640.0},
                {"planet_name": "Proxima b", "g_planet": 11.2, "cp_planet": 980.0},
                {"planet_name": "Kepler-22b", "g_planet": 14.0, "cp_planet": 1200.0},
                {"planet_name": "Kepler-452b", "g_planet": 19.6, "cp_planet": 1100.0},
                {"planet_name": "Kepler-186f", "g_planet": 6.5, "cp_planet": 900.0},
                {"planet_name": "Gliese 581g", "g_planet": 8.0, "cp_planet": 950.0},
                {"planet_name": "Gliese 667Cc", "g_planet": 7.0, "cp_planet": 890.0},
                {"planet_name": "TRAPPIST-1d", "g_planet": 4.0, "cp_planet": 860.0},
                {"planet_name": "TRAPPIST-1e", "g_planet": 5.1, "cp_planet": 910.0},
                {"planet_name": "TRAPPIST-1f", "g_planet": 6.3, "cp_planet": 940.0},
                {"planet_name": "TRAPPIST-1g", "g_planet": 7.0, "cp_planet": 980.0},
                {"planet_name": "Barnard's Star b", "g_planet": 11.4, "cp_planet": 1050.0},
                {"planet_name": "LHS 1140b", "g_planet": 16.1, "cp_planet": 1150.0},
                {"planet_name": "TOI 700d", "g_planet": 8.6, "cp_planet": 1000.0},
                {"planet_name": "K2-18b", "g_planet": 12.2, "cp_planet": 1080.0},
                {"planet_name": "55 Cancri e", "g_planet": 15.0, "cp_planet": 1200.0},
                {"planet_name": "WASP-12b", "g_planet": 18.3, "cp_planet": 1400.0},
                {"planet_name": "WASP-17b", "g_planet": 9.4, "cp_planet": 1100.0},
                {"planet_name": "WASP-39b", "g_planet": 6.9, "cp_planet": 980.0},
                {"planet_name": "HD 209458b", "g_planet": 9.4, "cp_planet": 950.0},
                {"planet_name": "HR 8799e", "g_planet": 11.0, "cp_planet": 1020.0},
                {"planet_name": "Fomalhaut b", "g_planet": 12.0, "cp_planet": 1080.0},
                {"planet_name": "PSR B1257+12c", "g_planet": 7.6, "cp_planet": 870.0},
                {"planet_name": "PSR B1620-26 b", "g_planet": 10.8, "cp_planet": 1020.0},
                {"planet_name": "Kepler-10b", "g_planet": 19.8, "cp_planet": 1300.0},
                {"planet_name": "Kepler-69c", "g_planet": 10.5, "cp_planet": 1000.0},
                {"planet_name": "Kepler-62f", "g_planet": 6.3, "cp_planet": 940.0},
                {"planet_name": "Kepler-452b", "g_planet": 19.6, "cp_planet": 1150.0},
                {"planet_name": "Ross 128b", "g_planet": 9.1, "cp_planet": 950.0},
                {"planet_name": "GJ 1214b", "g_planet": 8.3, "cp_planet": 920.0},
                {"planet_name": "Wolf 1061c", "g_planet": 7.0, "cp_planet": 900.0},
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