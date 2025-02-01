import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer

class Question10(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
A locomotive of {mass} kg mass travels {velocity} m/s along a straight horizontal track at {latitude} degrees N. 
What lateral force is exerted on the rails? Compare the magnitudes of the upward reaction force exerted by the rails 
for cases where the locomotive is traveling eastward and westward, respectively.
        """
        self.func = self.calculate_coriolis_effect
        self.default_variables = {
            "mass": 2e5,        # Mass of the locomotive in kg
            "velocity": 50.0,   # Velocity of the locomotive in m/s
            "latitude": 43.0,   # Latitude in degrees
        }

        self.constant = {
            "g": 9.8,           # Gravitational acceleration in m/s^2
            "omega": 7.2921e-5  # Angular velocity of Earth in rad/s
        }

        self.independent_variables = {
            "mass": {"min": 1e4, "max": 5e5, "granularity": 1e4},
            "velocity": {"min": 1, "max": 100, "granularity": 1},
            "latitude": {"min": -90, "max": 90, "granularity": 0.1},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = []

        super(Question10, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_coriolis_effect(mass, velocity, latitude, g, omega):
        """
        Calculate the lateral force due to the Coriolis effect and the difference
        in upward reaction forces for eastward and westward travel.

        Parameters:
            mass (float): Mass of the locomotive in kg.
            velocity (float): Velocity of the locomotive in m/s.
            latitude (float): Latitude in degrees (positive for north, negative for south).
            g (float): Gravitational acceleration in m/s^2.
            omega (float): Angular velocity of Earth in rad/s.

        Returns:
            dict: A dictionary containing:
                  - Lateral force (N)
                  - Upward reaction force for eastward travel (N)
                  - Upward reaction force for westward travel (N)
                  - Difference in upward reaction force (N)
        """
        import math

        # Convert latitude to radians
        phi = math.radians(latitude)

        # Lateral force due to Coriolis effect
        f_coriolis = -mass * 2 * omega * velocity * math.sin(phi)

        # Upward reaction forces
        upward_reaction_eastward = mass * (g - 2 * omega * velocity * math.cos(phi))
        upward_reaction_westward = mass * (g + 2 * omega * velocity * math.cos(phi))

        # Difference in upward reaction force
        delta_upward_reaction = upward_reaction_westward - upward_reaction_eastward

        return NestedAnswer({
            "Lateral Force (N)": Answer(f_coriolis, "N", -3),
            "Upward Reaction Force (Eastward) (N)": Answer(upward_reaction_eastward, "N", -3),
            "Upward Reaction Force (Westward) (N)": Answer(upward_reaction_westward, "N", -3),
            "Difference in Upward Reaction Force (N)": Answer(delta_upward_reaction, "N", -3)
        })


if __name__ == '__main__':
    q = Question10(unique_id="q")
    print(q.question())
    print(q.answer())