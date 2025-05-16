import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question81(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """Consider a rectangular open channel with a width of {b} meters that transports water at a depth of {y} meters. Given that the channel slope is {S} and Manning's roughness coefficient is {n}, determine the flow rate Q in cubic meters per second. Employ the SI units and use the hydraulic radius R={R} m."""
        self.func = self.calculate_flow_rate_mannings
        self.default_variables = {
            "b": 3.0,       # Channel width in meters
            "y": 1.2,       # Water depth in meters
            "S": 0.0015,    # Channel slope
            "n": 0.015,     # Manning's roughness coefficient
            "R": 0.6667     # Hydraulic radius in meters
        }

        self.constant = {
            # "phi": 1.0      # SI unit system constant
        }

        self.independent_variables = {
            "b": {"min": 0.5, "max": 10.0, "granularity": 0.1},
            "y": {"min": 0.1, "max": 5.0, "granularity": 0.1},
            "S": {"min": 0.0001, "max": 0.01, "granularity": 0.0001},
            "n": {"min": 0.01, "max": 0.05, "granularity": 0.001},
        }

        self.dependent_variables = {
            "R": lambda vars: (vars["b"] * vars["y"]) / (vars["b"] + 2 * vars["y"])  # Hydraulic radius for rectangular channel
        }

        self.choice_variables = {
        }

        self.custom_constraints = [
            lambda vars, res: res > 0
        ]

        super(Question81, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_flow_rate_mannings(b, y, S, n, R):
        """
        Calculate the flow rate Q using Manning's equation.

        Parameters:
        - b (float): Channel width in meters
        - y (float): Water depth in meters
        - S (float): Channel slope (dimensionless)
        - n (float): Manning's roughness coefficient
        - R (float): Hydraulic radius in meters

        Returns:
        - Q (float): Flow rate in cubic meters per second
        """
        A = b * y
        # print(f"Area (A): {A} m^2")
        # print("R:", R)
        R_23 = R ** (2 / 3)
        # print(f"Hydraulic radius (R^2/3): {R_23} m^(2/3)")
        sqrt_S = S ** 0.5
        # print(f"Square root of slope (sqrt(S)): {sqrt_S} m^(1/2)")
        phi = 1.0  # SI units
        Q = (phi / n) * A * R_23 * sqrt_S
        return Answer(Q, "m^3/s", 3)


if __name__ == '__main__':
    q = Question81(unique_id="q")
    print(q.question())
    print(q.answer())