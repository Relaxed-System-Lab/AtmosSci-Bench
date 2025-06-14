import random, math
from question import Question
from answer import Answer, NestedAnswer


class Question49(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """French researchers have designed a high-altitude balloon that maintains a nearly constant potential temperature while orbiting Earth. Suppose this balloon is situated in the lower equatorial stratosphere where the temperature is stable at {T} K. If the balloon is vertically displaced from its equilibrium position by a small distance $\delta_z$, it would oscillate around the equilibrium point. What is the period of this oscillation?"""
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