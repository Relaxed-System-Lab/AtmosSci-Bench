import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question40(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """Find the horizontal displacement of a body dropped from a fixed platform at a height h at the equator neglecting the effects of air resistance. What is the numerical value of the displacement for h={h}m?"""
        self.func = self.calculate_horizontal_displacement
        self.default_variables = {
            "h": 5000,  # Height in meters
        }
        self.constant = {
            "g": 9.81,  # Gravitational acceleration (m/s^2)
            "omega": 7.2921e-5  # Earth's angular velocity (rad/s)
        }
        self.independent_variables = {
            "h": {"min": 1000, "max": 10000, "granularity": 1},  # Height in meters
        }
        self.dependent_variables = {
        }
        self.choice_variables = {}
        self.custom_constraints = [
            lambda vars, res: res > 0  # Horizontal displacement must be positive
        ]

        super(Question40, self).__init__(unique_id, seed, variables)



    @staticmethod
    def calculate_horizontal_displacement(h, g, omega):
        """
        Calculate the horizontal displacement of a body dropped from a height at the equator.

        Parameters:
        h (float): Height of the drop in meters.
        g (float): Acceleration due to gravity in m/s^2.
        omega (float): Angular velocity of Earth in rad/s.

        Returns:
        float: Horizontal displacement in meters.
        """
        # Calculate the total time of fall
        t_0 = (2 * h / g) ** 0.5

        # Calculate the horizontal displacement
        x = (omega * g / 3) * t_0 ** 3

        return Answer(x, "m", 1)



if __name__ == '__main__':
    q = Question40(unique_id="q")
    print(q.question())
    print(q.answer())