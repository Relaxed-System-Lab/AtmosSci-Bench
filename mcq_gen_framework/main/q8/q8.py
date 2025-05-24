import random, math
from question import Question
from answer import Answer

class Question8(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
#         self.template = """As a train traverses a curved path at a speed of {speed} m/s, a passenger standing on scales notes that his weight is {weight_increase_percentage}% higher than when the train is stationary. The track is inclined such that the force exerted on the passenger is perpendicular to the train's floor. Determine the curvature radius of the track."""
        self.template = """A train is running smoothly along a curved track at the rate of {speed} m/s. 
A passenger standing on a set of scales observes that his weight is {weight_increase_percentage}% 
greater than when the train is at rest. The track is banked so that the force acting on the passenger 
is normal to the floor of the train. What is the radius of curvature of the track?
"""
        self.func = self.calculate_radius_of_curvature
        self.default_variables = {
            "speed": 50.0,  # Train speed (m/s)
            "weight_increase_percentage": 10.0,  # Percentage increase in observed weight
        }

        self.constant = {
            "gravity": 9.81  # Gravitational acceleration (m/s^2)
        }

        self.independent_variables = {
            "speed": {"min": 1.0, "max": 100.0, "granularity": 1.0},
            "weight_increase_percentage": {"min": 0.1, "max": 50.0, "granularity": 0.1},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = []

        super(Question8, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_radius_of_curvature(speed, weight_increase_percentage, gravity):
        """
        Calculate the radius of curvature of the track.

        Parameters:
        speed (float): Speed of the train in m/s.
        weight_increase_percentage (float): Percentage increase in weight observed on the scales.
        gravity (float): Gravitational acceleration in m/s^2.

        Returns:
        float: Radius of curvature in meters.
        """
        # Convert percentage increase to a multiplier
        weight_multiplier = 1 + (weight_increase_percentage / 100)

        # Solve for the radius using the given formula
        radius = speed**2 / (gravity * ((weight_multiplier**2 - 1) ** 0.5))

        return Answer(radius, "m", 2)

if __name__ == '__main__':
    q = Question8(unique_id="q")
    print(q.question())
    print(q.answer())