import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question82(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """A rectangular channel with a width of {b} m conveys a flow rate of {Q} m³/s at a depth of {y1} m. There is a plan to build a hump at a certain section. Calculate the water surface levels both upstream from the hump and directly over the hump if the hump's height is a) {delta_z1} m and b) {delta_z2} m (assuming no energy loss at the hump)."""
        self.func = self.calculate_water_surface_elevations
        self.default_variables = {
            "b": 4.0,             # channel width (m)
            "Q": 20.0,            # discharge (m^3/s)
            "y1": 2.0,            # initial depth (m)
            "delta_z1": 0.33,     # hump height for case a (m)
            "delta_z2": 0.2       # hump height for case b (m)
        }

        self.constant = {
            # "g": 9.81  # gravitational acceleration (m/s^2)
        }

        self.independent_variables = {
            "b": {"min": 2.0, "max": 10.0, "granularity": 0.1},
            "Q": {"min": 5.0, "max": 50.0, "granularity": 0.1},
            "y1": {"min": 0.5, "max": 5.0, "granularity": 0.01}
        }

        self.dependent_variables = {
            "delta_z1": lambda vars: round(min(0.8, 0.4 * vars["y1"]), 2),
            "delta_z2": lambda vars: round(min(0.5, 0.2 * vars["y1"]), 2)
        }

        self.choice_variables = {
            # No grouped choices needed for this example
        }

        self.custom_constraints = [
            lambda vars, res: vars["delta_z1"] > vars["delta_z2"]
        ]

        super(Question82, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_water_surface_elevations(b, Q, y1, delta_z1, delta_z2):
        """
        Calculates the upstream and downstream water surface elevations for two hump heights.
        """
        import math
        from scipy.optimize import fsolve

        g = 9.81

        def compute(y1, delta_z):
            v1 = Q / (b * y1)
            E1 = y1 + v1**2 / (2 * g)
            yc = (Q**2 / (b**2 * g)) ** (1/3)
            Ec = 1.5 * yc
            E2 = E1 - delta_z

            if E2 < Ec:
                def eqn(y):
                    return y + Q**2 / (2 * g * b**2 * y**2) - (Ec + delta_z)
                y1_prime = fsolve(eqn, y1 + 0.1)[0]
                y2 = yc
            else:
                def eqn(y):
                    return y + Q**2 / (2 * g * b**2 * y**2) - E2
                y2 = fsolve(eqn, y1)[0]
                y1_prime = y1
            return y1_prime, y2 + delta_z

        y1_prime_a, ws_hump_a = compute(y1, delta_z1)
        y1_prime_b, ws_hump_b = compute(y1, delta_z2)

        return NestedAnswer({
            "(a)": NestedAnswer({
                "Upstream": Answer(y1_prime_a, "m", 3),
                "over the hump": Answer(ws_hump_a, "m", 3)
            }),
            "(b)": NestedAnswer({
                "Upstream": Answer(y1_prime_b, "m", 3),
                "over the hump": Answer(ws_hump_b, "m", 3)
            })
        })

if __name__ == '__main__':
    q = Question82(unique_id="q")
    print(q.question())
    print(q.answer())