import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question103(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """A hydrologist analyzing runoff production within a catchment records these chloride concentrations at the height of a rainstorm: $C_n={C_n}$ μmol/L, $C_o={C_o}$ μmol/L, and $C_t={C_t}$ μmol/L. Determine the proportions of total streamflow that are provided by new water and old water."""

        self.func = self.calculate_water_fractions

        self.default_variables = {
            "C_n": 4.5,   # Chloride concentration in new water (μmol/L)
            "C_o": 40.5,  # Chloride concentration in old water (μmol/L)
            "C_t": 36.0   # Chloride concentration in total streamflow (μmol/L)
        }

        self.constant = {}

        self.independent_variables = {
            "C_n": {"min": 0.1, "max": 20.0, "granularity": 0.1},
            "C_o": {"min": 25.0, "max": 60.0, "granularity": 0.1},
        }

        self.dependent_variables = {
            "C_t": lambda vars: round(
                vars["C_o"] - 0.1 * abs(vars["C_n"] - vars["C_o"]),
                2
            )  # Ensure C_t is between C_o and C_n to simulate mixture
        }

        self.choice_variables = {
        }

        self.custom_constraints = [
            lambda vars, res: vars["C_n"] != vars["C_o"],  # avoid zero division
            lambda vars, res: 0 <= res["new_water_fraction"].value <= 1 and 0 <= res["old_water_fraction"].value <= 1,  # fractions should be in [0, 1]
            lambda vars, res: abs(res["new_water_fraction"].value + res["old_water_fraction"].value - 1.0) < 1e-6  # sum to 1
        ]

        super(Question103, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_water_fractions(C_n, C_o, C_t):
        """
        Calculates the fractions of new and old water in total streamflow based on chloride concentrations.

        Parameters:
        - C_n (float): Chloride concentration in new water (μmol/L)
        - C_o (float): Chloride concentration in old water (μmol/L)
        - C_t (float): Chloride concentration in total streamflow (μmol/L)

        Returns:
        - (float, float): Tuple containing (fraction of new water, fraction of old water)
        """
        if C_n == C_o:
            raise ValueError("C_n and C_o cannot be equal; division by zero would occur.")

        Q_n_fraction = (C_t - C_o) / (C_n - C_o)
        Q_o_fraction = 1 - Q_n_fraction

        return NestedAnswer({
            "new_water_fraction": Answer(Q_n_fraction, "", 3),
            "old_water_fraction": Answer(Q_o_fraction, "", 3)
        })

if __name__ == '__main__':
    q = Question103(unique_id="q")
    print(q.question())
    print(q.answer())