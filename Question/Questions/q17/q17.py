import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question17(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """What is the circulation about a square of {square_side_km} km on a side for an easterly (that is, westward flowing) wind that decreases in magnitude toward the north at a rate of {wind_change_rate} m/s per {change_distance_km} km? What is the mean relative vorticity in the square?"""
        self.func = self.calculate_circulation_and_vorticity
        self.default_variables = {
            "square_side_km": 1000,  # Side length of the square in kilometers
            "wind_change_rate": 10,  # Change in wind speed in m/s
            "change_distance_km": 500  # Distance over which the wind changes in kilometers
        }
        self.independent_variables = {
            "square_side_km": {"min": 100, "max": 2000, "granularity": 10},
            "wind_change_rate": {"min": 1, "max": 20, "granularity": 1},
            "change_distance_km": {"min": 100, "max": 1000, "granularity": 100}
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["change_distance_km"] > 0 and vars["square_side_km"] > 0
        ]

        super(Question17, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_circulation_and_vorticity(square_side_km, wind_change_rate, change_distance_km):
        """
        Calculate the circulation and mean relative vorticity over a square.

        Parameters:
            square_side_km (float): Side length of the square in kilometers.
            wind_change_rate (float): Change in wind speed in m/s.
            change_distance_km (float): Distance over which the wind changes in kilometers.

        Returns:
            dict: A dictionary containing circulation (in m^2/s) and mean relative vorticity (in 1/s).
        """
        # Convert square side and change distance to meters
        square_side_m = square_side_km * 1000
        change_distance_m = change_distance_km * 1000

        # Calculate mean relative vorticity (zeta)
        vorticity = -wind_change_rate / change_distance_m

        # Calculate circulation (C)
        area = square_side_m ** 2
        circulation = vorticity * area

        return NestedAnswer({
            "mean_relative_vorticity": Answer(vorticity, "s^-1", None),  # Vorticity in 1/s
            "circulation": Answer(circulation, "m^2/s", 0),  # Circulation in m^2/s
        })


if __name__ == '__main__':
    q = Question17(unique_id="q")
    print(q.question())
    print(q.answer())