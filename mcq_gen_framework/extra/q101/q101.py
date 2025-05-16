import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question101(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """You are tasked with designing a basic filtration system for a community's water supply using cylindrical sand columns (K={K} m/day). The filter must be {L} m in length to effectively capture particulates in the water. Since the system will operate via gravity, the pressure heads at the top and bottom of the vertically-oriented filter will be {head_top} m and {head_bottom} m, respectively.  
(a). What diameter is necessary for the filter to process {Q_gpd} gallons of water per day? Is this dimension feasible (anything exceeding about {max_diameter} m is not feasible)?  
(b). Evaluate each of the following alternatives and consider adjustments to your design:  
i. Extend the sand filter (to what length?)  
ii. Increase the hydraulic head at the inflow (by how much?)  
iii. Implement multiple filters (how many? what dimensions?)"""
        self.func = self.calculate_filter_design
        self.default_variables = {
            "Q_gpd": 4000,           # Flow in gallons per day
            "K": 5.0,                # Hydraulic conductivity (m/day)
            "L": 3.0,                # Filter length (m)
            "head_top": 0.0,         # Hydraulic head at inflow (m)
            "head_bottom": 0.0,      # Hydraulic head at outflow (m)
            "max_diameter": 1.0      # Maximum feasible diameter (m)
        }

        self.constant = {
            # "gallon_to_m3": 1 / 264.2
        }

        self.independent_variables = {
            "Q_gpd": {"min": 500, "max": 10000, "granularity": 100},
            "K": {"min": 0.1, "max": 10.0, "granularity": 0.1},
            "L": {"min": 0.5, "max": 5.0, "granularity": 0.1},
            "head_top": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "head_bottom": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "max_diameter": {"min": 0.1, "max": 2.0, "granularity": 0.1}
        }

        self.dependent_variables = {
            # "hydraulic_gradient": lambda v: (v["head_top"] - v["head_bottom"]) / v["L"] if v["L"] != 0 else 1.0
        }

        self.choice_variables = {
            # "filter_material": [
            #     {"material": "Coarse Sand", "K": 10.0},
            #     {"material": "Medium Sand", "K": 5.0},
            #     {"material": "Fine Sand", "K": 1.0}
            # ]
        }

        self.custom_constraints = [
            lambda v, r: v["head_top"] >= v["head_bottom"],
            lambda v, r: r["(a)"]["diameter"] >= 0,  # diameter non-negative
            lambda v, r: v["L"] > 0
        ]

        super(Question101, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_filter_design(Q_gpd, K, L, head_top, head_bottom, max_diameter):
        """
        Calculates required filter diameter, feasibility, required head for feasible diameter,
        and number of max-diameter filters needed.
        """
        gallon_to_m3 = 1 / 264.2
        Q_m3_day = Q_gpd * gallon_to_m3

        hydraulic_gradient = (head_top - head_bottom) / L if L != 0 else 1.0
        if hydraulic_gradient == 0:
            hydraulic_gradient = 1.0

        A = Q_m3_day / (K * hydraulic_gradient)
        D = math.sqrt(4 * A / math.pi)

        is_feasible = D <= max_diameter

        max_A = math.pi * (max_diameter / 2) ** 2
        required_gradient = Q_m3_day / (K * max_A)
        required_head = required_gradient * L

        Q_per_filter = K * max_A * hydraulic_gradient
        num_filters = math.ceil(Q_m3_day / Q_per_filter)

        return NestedAnswer({
            "(a)": NestedAnswer({
                "diameter": Answer(D, "m", 2),
                "feasible": Answer(is_feasible, "", None)
            }),
            "(b)": NestedAnswer({
                "(i)": Answer(L, "m", 2),
                "(ii)": Answer(required_head, "m", 2),
                "(iii)": Answer(num_filters, "", None)
            })
        })

if __name__ == '__main__':
    q = Question101(unique_id="q")
    print(q.question())
    print(q.answer())