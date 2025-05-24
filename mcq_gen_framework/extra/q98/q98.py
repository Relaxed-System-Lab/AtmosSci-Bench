import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question98(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """The pressure decrease across a properly designed constriction can be utilized to determine the flow velocity in a pipe. Given that the pressure drop from a {d1_m}-m diameter section to a {d2_m}-m diameter section is {pressure_drop_pa} Pa, what is the flow velocity (m/s) in the {d1_m}-m diameter section of the pipe? Hint: Apply the conservation of mass equation to connect the velocity at the smaller section with that at the larger section."""

        self.func = self.calculate_velocity_in_wide_section

        self.default_variables = {
            "d1_m": 0.1,                 # Diameter of wide section (m)
            "d2_m": 0.05,                # Diameter of narrow section (m)
            "pressure_drop_pa": 7500,   # Pressure drop from d1 to d2 (Pa)
        }

        self.constant = {
        }

        self.independent_variables = {
            "d1_m": {"min": 0.05, "max": 1.0, "granularity": 0.01},
            "d2_m": {"min": 0.01, "max": 0.99, "granularity": 0.01},
            "pressure_drop_pa": {"min": 100, "max": 20000, "granularity": 10},
        }

        self.dependent_variables = {}

        self.choice_variables = {

        }

        self.custom_constraints = [
            lambda vars, res: vars["d2_m"] < vars["d1_m"]  # Ensure narrowing occurs
        ]


        super(Question98, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_velocity_in_wide_section(d1_m, d2_m, pressure_drop_pa):
        """
        Calculate the velocity in the wider section of a pipe using Bernoulli's equation and conservation of mass.

        Parameters:
        - d1_m: Diameter of the wider section (m)
        - d2_m: Diameter of the narrower section (m)
        - pressure_drop_pa: Pressure drop from d1 to d2 (Pa)

        Returns:
        - U1: Velocity in the wider section (m/s)
        """

        density_kg_m3 = 1000        # Fluid density (kg/m^3)
        # Velocity ratio from continuity equation
        velocity_ratio = (d1_m / d2_m) ** 2

        # Bernoulli + continuity gives:
        # ΔP = (1/2) * ρ * (U2^2 - U1^2)
        #     = (1/2) * ρ * ((velocity_ratio^2 - 1) * U1^2)
        coeff = 0.5 * density_kg_m3 * (velocity_ratio ** 2 - 1)
        U1 = (pressure_drop_pa / coeff) ** 0.5

        return Answer(U1, "m/s", 3)


if __name__ == '__main__':
    q = Question98(unique_id="q")
    print(q.question())
    print(q.answer())