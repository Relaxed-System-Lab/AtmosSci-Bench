import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question65(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """
Suppose that the mass of air in an entraining cumulus updraft increases exponentially with height so that $m=m_{{0}} e^{{z / H}}$, where H={H} km and $m_{{0}}$ is the mass at a reference level. If the updraft speed is {w_reference} m/s at {z_reference} km height, what is its value at a height of {z_target} km assuming that the updraft has zero net buoyancy?
        """
        self.func = self.calculate_updraft_speed

        self.default_variables = {
            "w_reference": 3.0,  # Updraft speed at reference height (m/s)
            "z_reference": 2.0,  # Reference height (km)
            "z_target": 8.0,  # Target height (km)
            "H": 8.0,  # Scale height for the exponential mass distribution (km)
        }

        self.constant = {}

        self.independent_variables = {
            "w_reference": {"min": 0.1, "max": 20.0, "granularity": 0.1},
            "z_reference": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "H": {"min": 1.0, "max": 20.0, "granularity": 0.1},
        }

        self.dependent_variables = {
            "z_target": lambda vars: vars["z_reference"] + 6.0,  # Ensure z_target > z_reference
        }

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["z_reference"] < vars["z_target"]  # Reference height must be less than target height
        ]

        super(Question65, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_updraft_speed(w_reference, z_reference, z_target, H):
        """
        Calculate the updraft speed at a target height given the reference speed and height.

        Parameters:
        - w_reference: Updraft speed at the reference height (m/s)
        - z_reference: Reference height (km)
        - z_target: Target height (km)
        - H: Scale height for the exponential mass distribution (km)

        Returns:
        - Updraft speed at the target height (m/s)
        """
        import math

        # Calculate the change in ln(w^2) between the reference height and target height
        delta_ln_w2 = -2 * (z_target - z_reference) / H

        # Compute the updraft speed at the target height
        w_target = w_reference * math.exp(0.5 * delta_ln_w2)

        return Answer(w_target, "m/s", 2)


if __name__ == '__main__':
    q = Question65(unique_id="q")
    print(q.question())
    print(q.answer())