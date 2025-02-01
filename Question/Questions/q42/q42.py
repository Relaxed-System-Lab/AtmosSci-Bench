import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question42(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """Isolines of {p1}-{p2} hPa thickness are drawn on a weather map using a contour interval of {delta_Z} m. 
What is the corresponding layer mean temperature interval?
"""
        self.func = self.calculate_temperature_interval

        self.default_variables = {
            "delta_Z": 60.0,  # Thickness contour interval (m)
            "p1": 1000.0,  # Lower pressure level (hPa)
            "p2": 500.0  # Upper pressure level (hPa)
        }

        self.constant = {
            "R": 287.0,  # Specific gas constant for dry air (J/(kg*K))
            "g0": 9.8,  # Gravitational acceleration (m/s^2)
            }

        self.independent_variables = {
            "delta_Z": {"min": 10.0, "max": 100.0, "granularity": 1.0},
            "p1": {"min": 800.0, "max": 1200.0, "granularity": 10.0},
            "p2": {"min": 200.0, "max": 800.0, "granularity": 10.0}
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["p1"] > vars["p2"],  # Lower pressure must be greater than upper pressure
        ]

        super(Question42, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_temperature_interval(delta_Z, R, g0, p1, p2):
        """
        Calculate the layer mean temperature interval using:
        delta_T = (g0 * delta_Z) / (R * ln(p1 / p2))

        Parameters:
        delta_Z (float): Thickness contour interval (m)
        R (float): Specific gas constant for dry air (J/(kg*K))
        g0 (float): Gravitational acceleration (m/s^2)
        p1 (float): Lower pressure level (hPa)
        p2 (float): Upper pressure level (hPa)

        Returns:
        float: Layer mean temperature interval (°C)
        """
        # Calculate the natural logarithm of the pressure ratio
        ln_pressure_ratio = math.log(p1 / p2)

        # Calculate the temperature interval
        delta_T = (g0 * delta_Z) / (R * ln_pressure_ratio)

        return Answer(delta_T, "°C", 2)



if __name__ == '__main__':
    q = Question42(unique_id="q")
    print(q.question())
    print(q.answer())