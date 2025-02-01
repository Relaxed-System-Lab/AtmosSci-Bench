import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question49(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """ 
French scientists have developed a high-altitude balloon that remains approximately at constant potential temperature as it circles Earth. 
Suppose such a balloon is in the lower equatorial stratosphere where the temperature is isothermal at {T} K. 
If the balloon were displaced vertically from its equilibrium level by a small distance $\delta_z$, it would tend to oscillate about the equilibrium level. 
What is the period of this oscillation?
        """
        self.func = self.calculate_period

        self.default_variables = {
            "T": 200,            # Isothermal temperature (K)
        #   "delta_z": 10.0      # Small displacement (m)
        }

        self.constant = {
            "g": 9.8,            # Gravitational acceleration (m/s^2)
            "cp": 1003,          # Specific heat capacity at constant pressure (J/(kg*K))

        }

        self.independent_variables = {
        #   "cp": {"min": 900, "max": 1100, "granularity": 1},
            "T": {"min": 190, "max": 210, "granularity": 1},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = []

        super(Question49, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_period(g, cp, T):
        """
        Calculate the period of oscillation for a high-altitude balloon.

        Parameters:
        g (float): Gravitational acceleration (m/s^2).
        cp (float): Specific heat capacity at constant pressure (J/(kg*K)).
        T (float): Isothermal temperature (K).

        Returns:
        float: Period of oscillation (seconds).
        """
        import math

        # Logarithmic potential temperature gradient
        dln_theta_dz = g / (cp * T)

        # Buoyancy frequency (N)
        N = math.sqrt(g * dln_theta_dz)

        # Period of oscillation
        period = 2 * math.pi / N
        return Answer(period, "s", 0)


if __name__ == '__main__':
    q = Question49(unique_id="q")
    print(q.question())
    print(q.answer())