import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question50(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """The actual wind is directed {angle_degrees}° to the right of the geostrophic wind. 
 If the geostrophic wind is {geostrophic_wind_speed} m/s, what is the rate of change of wind speed? Let f={coriolis_parameter} s^-1."""
        self.func = self.calculate_wind_speed_change
        self.default_variables = {
            "geostrophic_wind_speed": 20.0,  # m/s
            "angle_degrees": 30.0           # degrees
        }
        self.constant = {
            "coriolis_parameter": 1e-4,     # s^-1
        }
        self.independent_variables = {
            "geostrophic_wind_speed": {"min": 5.0, "max": 50.0, "granularity": 0.1},
            "angle_degrees": {"min": 0.0, "max": 90.0, "granularity": 1.0},
        }
        self.dependent_variables = {}
        self.choice_variables = {}
        self.custom_constraints = [
            lambda vars, res: -1e-2 <= res <= 0,  # Ensures the rate of change is negative and within a reasonable range
        ]
        super(Question50, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_wind_speed_change(geostrophic_wind_speed, coriolis_parameter, angle_degrees):
        """
        Calculate the rate of change of wind speed (DV/Dt).
        
        Parameters:
        geostrophic_wind_speed (float): Geostrophic wind speed (|Vg|) in m/s.
        coriolis_parameter (float): Coriolis parameter (f) in s^-1.
        angle_degrees (float): Angle between the geostrophic and actual wind in degrees.
        
        Returns:
        float: Rate of change of wind speed in m/s².
        """
        import math
        # Convert angle to radians
        angle_radians = math.radians(angle_degrees)
        # Compute rate of change of wind speed
        return Answer(-coriolis_parameter * geostrophic_wind_speed * math.sin(angle_radians), "m/s^2", 6)


if __name__ == '__main__':
    q = Question50(unique_id="q")
    print(q.question())
    print(q.answer())