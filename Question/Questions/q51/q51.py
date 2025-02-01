import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question51(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
Determine the radii of curvature for the trajectories of air parcels located {distance} km to the east, north, south, and west of the center of a circular low-pressure system, respectively. 
The system is moving eastward at {c} m/s. Assume geostrophic flow with a uniform tangential wind speed of {V} m/s.
        """
        self.func = self.calculate_radii_of_curvature

        self.default_variables = {
            "distance": 500.0,  # Distance from the center (km)
            "c": 15.0,          # System speed (m/s)
            "V": 15.0,          # Tangential wind speed (m/s)
        }

        self.constant = {}

        self.independent_variables = {
            "distance": {"min": 100.0, "max": 1000.0, "granularity": 10.0},
            "c": {"min": 5.0, "max": 30.0, "granularity": 1.0},
            "V": {"min": 5.0, "max": 30.0, "granularity": 1.0},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
        #   lambda vars, res: vars["V"] > vars["c"]  # Wind speed must exceed system speed
        ]


        super(Question51, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_radii_of_curvature(distance, c, V):
        """
        Calculate the radii of curvature for trajectories at four directions around the center.

        Parameters:
        - distance (float): Radius of the system (km).
        - c (float): Speed of the system (m/s).
        - V (float): Tangential wind speed (m/s).

        Returns:
        - dict: Radii of curvature for North, South, East, and West directions.
        """
        import math

        directions = {
            "North": math.pi,
            "South": 0,
            "East": math.pi / 2,
            "West": 3 * math.pi / 2
        }

        results = {}
        for direction, gamma in directions.items():
            if V == c * math.cos(gamma):  # Handle special case where R_t -> infinity
                results[direction] = float('inf')
            else:
                R_t = distance / (1 - (c * math.cos(gamma) / V))
                results[direction] = Answer(R_t, "km", 0)
        return NestedAnswer(results)


if __name__ == '__main__':
    q = Question51(unique_id="q")
    print(q.question())
    print(q.answer())