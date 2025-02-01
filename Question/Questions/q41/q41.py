import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question41(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """Calculate the {p1}-{p2} hPa thickness for isothermal conditions with temperatures of {temp1} K and {temp2} K, respectively."""
        self.func = self.calculate_thickness
        self.default_variables = {
            "temp1": 273.0,  # Temperature at the first pressure level in Kelvin
            "temp2": 250.0,  # Temperature at the second pressure level in Kelvin
            "p1": 1000.0,    # Higher pressure level in hPa
            "p2": 500.0      # Lower pressure level in hPa
        }

        self.constant = {
            "g0": 9.81,       # Gravitational acceleration in m/s²
            "R": 287.0,      # Specific gas constant in J/(kg·K)
        }

        self.independent_variables = {
            "temp1": {"min": 220.0, "max": 300.0, "granularity": 0.1},
            "temp2": {"min": 200.0, "max": 290.0, "granularity": 0.1},
            "p1": {"min": 800.0, "max": 1200.0, "granularity": 1.0},
            "p2": {"min": 400.0, "max": 800.0, "granularity": 1.0}
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["temp1"] > vars["temp2"],  # Ensure temp1 > temp2 for validity
            lambda vars, res: vars["p1"] > vars["p2"]        # Ensure p1 > p2 for physical validity
        ]

        super(Question41, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_thickness(temp1, temp2, R, g0, p1, p2):
        """
        Calculate the thickness for isothermal conditions between two pressure levels.

        Parameters:
            temp1 (float): Temperature at the first pressure level (in Kelvin).
            temp2 (float): Temperature at the second pressure level (in Kelvin).
            R (float): Specific gas constant (in J/(kg·K)).
            g0 (float): Gravitational acceleration (in m/s²).
            p1 (float): Higher pressure level (in hPa).
            p2 (float): Lower pressure level (in hPa).

        Returns:
            tuple: Thickness for temp1 and temp2, in meters.
        """
        ln_p1_p2 = math.log(p1 / p2)
        Z_T1 = (R * temp1 / g0) * ln_p1_p2
        Z_T2 = (R * temp2 / g0) * ln_p1_p2

        return NestedAnswer([Answer(Z_T1, "m", 1), Answer(Z_T2, "m", 1)])



if __name__ == '__main__':
    q = Question41(unique_id="q")
    print(q.question())
    print(q.answer())