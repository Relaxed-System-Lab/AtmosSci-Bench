import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question69(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """ 
Suppose that temperature increases linearly with height in the layer between {z0} and {zT} km 
at a rate of {gamma} K/km. If the temperature is {T0} K at {z0} km, find the value of the scale height H 
for which the log-pressure height z coincides with actual height at {zT} km. (Assume that z coincides 
with the actual height at {z0} km and let g be a constant.)
        """
        self.func = self.calculate_scale_height

        self.default_variables = {
            "z0": 20,        # Initial height (km)
            "zT": 50,        # Final height (km)
            "T0": 200,       # Temperature at z0 (K)
            "gamma": 2,   # Temperature lapse rate (K/km)
        }

        self.constant = {
            "R": 287,        # Specific gas constant (J/kg·K)
            "g": 9.81         # Gravitational acceleration (m/s²)
        }

        self.independent_variables = {
            "R": {"min": 200, "max": 400, "granularity": 1},
            "z0": {"min": 10, "max": 30, "granularity": 1},
            "zT": {"min": 40, "max": 60, "granularity": 1},
            "T0": {"min": 150, "max": 250, "granularity": 1},
            "gamma": {"min": 1, "max": 9, "granularity": 0.1},
        }

        self.dependent_variables = {
        #    "g": lambda vars: 9.8  # Gravitational acceleration remains constant
        }

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["zT"] > vars["z0"],  # zT must be greater than z0
        ]

        super(Question69, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_scale_height(R, z0, zT, T0, gamma, g):
        """
        Calculate the scale height H based on the given parameters.

        Parameters:
            R (float): Specific gas constant (J/kg·K).
            z0 (float): Initial height (km).
            zT (float): Final height (km).
            T0 (float): Temperature at z0 (K).
            gamma (float): Temperature lapse rate (K/km).
            g (float): Gravitational acceleration (m/s²).

        Returns:
            float: Scale height H (m).
        """
        # Convert heights to consistent units (meters)
        delta_z = zT - z0  # Difference in height (km)
        # z0_m = z0 * 1000
        # zT_m = zT * 1000

        # Temperature at zT
        T_T = T0 + gamma * (zT - z0)

        # Calculate scale height H
        H = (R * delta_z * gamma) / (g * math.log(T_T / T0))
        # print("T_T", T_T)

        # H_in_m = H * 1000
        return Answer(H, "m", 1)


if __name__ == '__main__':
    q = Question69(unique_id="q")
    print(q.question())
    print(q.answer())