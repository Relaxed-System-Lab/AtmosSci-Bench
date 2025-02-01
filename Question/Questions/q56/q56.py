import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question56(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
Suppose that during the passage of a cyclonic storm the radius of curvature of the isobars is observed to be {R_s} km 
at a station where the wind is veering (turning clockwise) at a rate of {wind_change_rate_deg_per_hour}° per hour. 
What is the radius of curvature of the trajectory for an air parcel that is passing over the station? 
(The wind speed is {V} m/s.)
        """
        self.func = self.calculate_trajectory_radius

        self.default_variables = {
            "R_s": 800.0,  # Radius of curvature of the isobars (km)
            "wind_change_rate_deg_per_hour": -10.0,  # Wind veering rate (deg/hour)
            "V": 20.0,  # Wind speed (m/s)
        }

        self.constant = {}

        self.independent_variables = {
            "R_s": {"min": 100.0, "max": 1000.0, "granularity": 1.0},
            "wind_change_rate_deg_per_hour": {"min": -20.0, "max": -1.0, "granularity": 0.1},
            "V": {"min": 5.0, "max": 50.0, "granularity": 0.1},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: res < 0,  # Resulting radius should be negative as per the example solution
        ]


        super(Question56, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_trajectory_radius(R_s, wind_change_rate_deg_per_hour, V):
        """
        Calculate the radius of curvature of the trajectory of an air parcel.

        Parameters:
        - R_s: Radius of curvature of the isobars (km)
        - wind_change_rate_deg_per_hour: Rate of change of wind direction (degrees/hour)
        - V: Wind speed (m/s)

        Returns:
        - R_t: Radius of curvature of the trajectory (km)
        """
        import math

        # Convert inputs to SI units and calculate
        R_s_m = R_s * 1000  # Convert R_s to meters
        wind_change_rate_rad_per_sec = (wind_change_rate_deg_per_hour * math.pi / 180) / 3600  # Convert to rad/s
        R_t_m = V / (wind_change_rate_rad_per_sec + V / R_s_m)  # Calculate R_t in meters
        R_t_km = R_t_m / 1000  # Convert to kilometers

        return Answer(R_t_km, "km", 0)


if __name__ == '__main__':
    q = Question56(unique_id="q")
    print(q.question())
    print(q.answer())