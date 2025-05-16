import random, math
from question import Question
from answer import Answer, NestedAnswer


class Question51(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """Calculate the radii of curvature for the paths of air parcels situated {distance} km in the east, north, south, and west directions from the center of a circular low-pressure system. The system is progressing eastward at {c} m/s. Assume geostrophic flow with a constant tangential wind speed of {V} m/s."""
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

        self.knowledge = """
Substituting the preceding equation into (3.23) and
solving for $R_{t}$ with the aid of (3.20), we obtain the desired relationship between the curvature of the streamlines and the curvature of the trajectories:

$$
\begin{equation*}
R_{t}=R_{S}\left(1-\frac{C \cos \gamma}{V}\right)^{-1} \tag{3.24}
\end{equation*}
$$

Equation (3.24) can be used to compute the curvature of the trajectory anywhere on a moving pattern of streamlines. In Figure 3.7 the curvatures of the trajectories for parcels initially located due north, east, south, and west of the center of a cyclonic system are shown both for the case of a wind speed greater than the speed of movement of the height contours and for the case of a wind speed less than the speed of movement of the height contours. In these examples the plotted trajectories are based on a geostrophic balance so that the height contours are equivalent to streamlines. It is also assumed for simplicity that the wind speed does not depend on the distance from the center of the system.
"""


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