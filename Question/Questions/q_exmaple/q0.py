import random
from ..question import Question

class Question0(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.template = """
        """
        self.func = self.calculate_excess_precipitation
        self.type = "earth_science"
        self.default_variables = {
            "f0": 8.0,  # Initial rate of infiltration (cm/hr)
            "fc": 0.5,  # Final infiltration capacity (cm/hr)
            "k": 0.4,   # Time constant (hr^-1)
            "t1": 2.0,  # Start time (hr)
            "t2": 5.0   # End time (hr)
        }
        self.independent_variables = {
            "f0": {"min": 0.1, "max": 20.0, "granularity": 0.1},
            "fc": {"min": 0.1, "max": 5.0, "granularity": 0.1},
            "k": {"min": 0.01, "max": 1.0, "granularity": 0.01},
            "t1": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "t2": {"min": 0.0, "max": 10.0, "granularity": 0.1}
        }

        self.dependent_variables = {
            "forest_percent": lambda vars: 100 - vars["open_space_percent"],
            "open_space_A_percent": lambda vars: 100 - vars["open_space_C_percent"],
        }

        self.choice_variables = {
            "planet": [
                {"planet_name": "Mercury", "D_v": 5.79e7},
                {"planet_name": "Venus", "D_v": 1.08e8}
            ]
        }

        self.custom_constraints = [
            lambda vars, res: vars["t1"] < vars["t2"],
            lambda vars, res: res['infiltration_capacity_t1'] > 0
        ]

        super(Question0, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_excess_precipitation(
        open_space_percent, soil_group_c_percent, soil_group_a_percent,
        forest_percent, curve_numbers, rainfall, la_factor
    ):
        pass

if __name__ == '__main__':
    q = Question0(unique_id="q")
    print(q.question())
    print(q.answer())