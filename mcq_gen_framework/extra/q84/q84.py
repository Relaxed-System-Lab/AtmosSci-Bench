import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question84(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """Water flowing in a broad channel encounters a hump {delta_z} m tall, with an initial velocity of {v1} m/sec and a depth of {y1} m. Calculate 
a) The water depth y2 above the hump and 
b) The height of the hump that would make the crest flow critical."""

        self.func = self.calculate_hump_flow

        self.default_variables = {
            "y1": 1.0,         # Upstream depth in meters
            "v1": 1.5,         # Upstream velocity in m/s
            "delta_z": 0.1     # Hump height in meters
        }

        self.constant = {
            "g": 9.81          # Acceleration due to gravity in m/s^2
        }

        self.independent_variables = {
            "y1": {"min": 0.5, "max": 5.0, "granularity": 0.1},
            "v1": {"min": 0.1, "max": 5.0, "granularity": 0.1},
            "delta_z": {"min": 0.01, "max": 1.0, "granularity": 0.01}
        }

        self.dependent_variables = {
            # None in this case – all inputs are independent
        }

        self.choice_variables = {
            # No multiple-choice constraints for this question
        }

        self.custom_constraints = [
            # Ensure flow is subcritical upstream (Fr1 < 1)
            lambda vars, res: (vars["v1"] / (self.constant["g"] * vars["y1"])**0.5) < 1.0,
            # Ensure delta_z is less than upstream specific energy
            lambda vars, res: vars["delta_z"] < vars["y1"] + (vars["v1"]**2) / (2 * self.constant["g"])
        ]

        super(Question84, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_hump_flow(y1, v1, delta_z, g):
        """
        Calculates:
        a) The water depth y2 over the hump
        b) The hump height that would cause critical flow over the crest

        Parameters:
        - y1: Upstream depth (m)
        - v1: Upstream velocity (m/s)
        - delta_z: Hump height (m)
        - g: Acceleration due to gravity (m/s^2)

        Returns:
        - (y2, delta_z_critical): Tuple of downstream depth and critical hump height
        """
        import numpy as np
        from scipy.optimize import fsolve

        # Upstream specific energy
        E1 = y1 + (v1 ** 2) / (2 * g)

        # Downstream specific energy
        E2 = E1 - delta_z

        # Critical depth
        yc = ((v1 ** 2 * y1 ** 2) / g) ** (1 / 3)

        # Critical specific energy
        Ec = 1.5 * yc

        # Energy equation: E2 = y2 + (y1^2 * v1^2) / (2 * g * y2^2)
        def energy_equation(y2):
            return y2 + (y1 ** 2 * v1 ** 2) / (2 * g * y2 ** 2) - E2

        # Solve for y2 (must be greater than yc)
        y2_initial = yc + 0.1
        y2_solution = fsolve(energy_equation, y2_initial)[0]

        # Critical hump height
        delta_z_critical = E1 - Ec

        return NestedAnswer({
            "y2": Answer(y2_solution, "m", 4),
            "delta_z_critical": Answer(delta_z_critical, "m", 4)
        })

if __name__ == '__main__':
    q = Question84(unique_id="q")
    print(q.question())
    print(q.answer())