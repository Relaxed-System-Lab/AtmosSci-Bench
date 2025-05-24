import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question85(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Physical Oceanography"
        self.template = """A smooth laminar boundary layer begins to form at the sharp leading edge of a propeller blade that is moving at {U} m/s relative to the {fluid_name}. Considering that the critical Reynolds number for flat plate turbulence is {Re_critical} based on the distance, x, from the leading edge, where should we expect the transition to turbulence to occur?"""

        self.func = self.calculate_transition_distance

        self.variables = ["U", "Re_critical", "nu", "fluid_name"]

        self.default_variables = {
            "U": 15.0,                  # Flow speed in m/s
            "Re_critical": 300000,      # Critical Reynolds number
            "nu": 1e-6,                 # Kinematic viscosity in m^2/s
            "fluid_name": "water"       # Name of the fluid
        }

        self.constant = {
            # No constants needed
        }

        self.independent_variables = {
            "U": {"min": 0.1, "max": 100.0, "granularity": 0.1},
            "Re_critical": {"min": 10000, "max": 1e6, "granularity": 1000}
        }

        self.dependent_variables = {
            # nu and fluid_name are selected together, not random
        }

        self.choice_variables = {
            "fluid": [
                {"fluid_name": "water", "nu": 1.0e-6},
                {"fluid_name": "air", "nu": 1.5e-5},
                {"fluid_name": "glycerin", "nu": 1.0e-3},
                {"fluid_name": "mercury", "nu": 1.2e-7},
                {"fluid_name": "ethanol", "nu": 1.2e-6},
                {"fluid_name": "methanol", "nu": 7.6e-7},
                {"fluid_name": "acetone", "nu": 3.2e-7},
                {"fluid_name": "benzene", "nu": 6.5e-7},
                {"fluid_name": "toluene", "nu": 7.3e-7},
                {"fluid_name": "diesel", "nu": 2.5e-6},
                {"fluid_name": "kerosene", "nu": 1.6e-6},
                {"fluid_name": "olive oil", "nu": 8.1e-5},
                {"fluid_name": "castor oil", "nu": 9.0e-4},
                {"fluid_name": "engine oil (10W-30)", "nu": 2.5e-4},
                {"fluid_name": "honey", "nu": 1.0e-2},
                {"fluid_name": "milk", "nu": 2.0e-6},
                {"fluid_name": "blood", "nu": 3.5e-6},
                {"fluid_name": "seawater", "nu": 1.2e-6},
                {"fluid_name": "helium", "nu": 1.0e-4},
                {"fluid_name": "hydrogen", "nu": 1.1e-4},
                {"fluid_name": "carbon dioxide", "nu": 1.4e-5},
                {"fluid_name": "ammonia", "nu": 1.4e-5},
                {"fluid_name": "butane", "nu": 7.0e-6},
                {"fluid_name": "propane", "nu": 8.0e-6},
                {"fluid_name": "nitrogen", "nu": 1.5e-5},
                {"fluid_name": "oxygen", "nu": 1.3e-5},
                {"fluid_name": "steam", "nu": 2.4e-5},
                {"fluid_name": "sulfuric acid", "nu": 2.5e-6},
                {"fluid_name": "acetylene", "nu": 1.3e-5},
                {"fluid_name": "chloroform", "nu": 4.5e-7}
            ]
        }

        self.custom_constraints = [
            lambda vars, res: res > 0 and res < 10  # distance should be within a physical range
        ]
        self.custom_constraints = [
            lambda vars, res: res > 0 and res < 10  # distance should be physically reasonable
        ]

        super(Question85, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_transition_distance(U, Re_critical, nu, fluid_name):
        """
        Calculate the distance from the leading edge at which transition to turbulence occurs
        in a laminar boundary layer based on critical Reynolds number.

        Parameters:
        - U (float): Flow velocity in m/s
        - Re_critical (float): Critical Reynolds number (dimensionless)
        - nu (float): Kinematic viscosity in m^2/s

        Returns:
        - x (float): Distance from the leading edge in meters
        """
        x = Re_critical * nu / U
        return Answer(x, "m", 3)

if __name__ == '__main__':
    q = Question85(unique_id="q")
    print(q.question())
    print(q.answer())