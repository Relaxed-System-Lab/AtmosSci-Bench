import random, math
from ..question import Question
from Questions.answer import Answer


class Question9(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
Two balls {diameter} meters in diameter are placed {distance} meters apart on a frictionless horizontal plane at {latitude}° latitude.
If the balls are impulsively propelled directly at each other with equal speeds, at what speed must they travel so that they just miss each other?
        """
        self.func = self.calculate_speed
        self.default_variables = {
            "diameter": 0.04,  # Diameter of the balls in meters
            "distance": 100.0,  # Initial separation in meters
            "latitude": 43.0,  # Latitude in degrees
        }

        self.constant = {
            "lateral_deflection": 0.02,  # Lateral deflection in meters
            "angular_velocity": 7.2921e-5  # Angular velocity of the Earth in radians per second
        }

        self.independent_variables = {
            "diameter": {"min": 0.01, "max": 1.0, "granularity": 0.01},
            "distance": {"min": 10.0, "max": 1000.0, "granularity": 1.0},
            "latitude": {"min": 0.0, "max": 90.0, "granularity": 0.1},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = []

        super(Question9, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_speed(diameter, distance, latitude, lateral_deflection, angular_velocity):
        """
        Calculate the speed required for two balls to just miss each other, considering Coriolis force.
        
        Parameters:
            diameter (float): Diameter of the balls in meters.
            distance (float): Initial separation between the balls in meters.
            latitude (float): Latitude in degrees.
            lateral_deflection (float): Lateral deflection for each ball in meters.
            angular_velocity (float): Angular velocity of the Earth in radians per second.

        Returns:
            float: Required speed in meters per second.
        """
        from mpmath import mp, radians, sin

        #    mpmath    
        mp.dps = 50  #         50  

        # Convert latitude to radians
        latitude_rad = radians(latitude)

        # Calculate the Coriolis acceleration term: 2 * Ω * sin(φ)
        coriolis_acceleration = 2 * angular_velocity * sin(latitude_rad)

        # Calculate time (t)
        time = 2 * lateral_deflection / (coriolis_acceleration * (distance / 2))

        # Calculate speed (u)
        speed = (distance / 2) / time

        return Answer(speed, "m/s", 2)

        # import math
        # # Convert latitude to radians
        # latitude_rad = math.radians(latitude)
        
        # # Calculate the Coriolis acceleration term: 2 * Ω * sin(φ)
        # coriolis_acceleration = 2 * angular_velocity * math.sin(latitude_rad)
        
        # # Calculate time (t)
        # time = 2 * lateral_deflection / (coriolis_acceleration * (distance / 2))
        
        # # Calculate speed (u)
        # speed = (distance / 2) / time
        
        # return speed

if __name__ == '__main__':
    q = Question9(unique_id="q")
    print(q.question())
    print(q.answer())