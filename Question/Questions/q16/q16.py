import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer

class Question16(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
A tornado rotates with constant angular velocity \omega. Show that the surface pressure at the center of the tornado is given by $p=p_{{0}} \\exp \\left(\\frac{{-\\omega^{{2}} r_{{0}}^{{2}}}}{{2 R T}} \\right)$, where $p_{{0}}$ is the surface pressure at a distance $r_{{0}}$ from the center and T is the temperature (assumed constant). If the temperature is {T} K, and pressure and wind speed at {r0} m from the center are {p0} hPa and {v} $\\mathrm{{~m}} \\mathrm{{~s}}^{{-1}}$, respectively, what is the central pressure?
        """
        self.func = self.calculate_central_pressure
        self.default_variables = {
        #   "omega": None,  # Angular velocity (rad/s)
            "r0": 100,      # Radius from the center (m)
        #    "R": 287,       # Specific gas constant for dry air (J/(kg*K))
            "T": 288,       # Temperature (K)
            "p0": 1000,     # Pressure at r0 (hPa)
            "v": 100        # Wind speed (m/s)
        }
        self.independent_variables = {
        #   "omega": {"min": 0.1, "max": 10.0, "granularity": 0.1},
            "r0": {"min": 10, "max": 1000, "granularity": 10},
            # "R": {"min": 200, "max": 300, "granularity": 10},
            "T": {"min": 100, "max": 400, "granularity": 10},
            "p0": {"min": 100, "max": 1100, "granularity": 100},
            "v": {"min": 10, "max": 200, "granularity": 5}
        }

        self.constant = {
            "R": 287  # the specific gas constant for dry air
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
        #    lambda vars, res: vars["p0"] > 0,  # Pressure must be positive
        #    lambda vars, res: vars["T"] > 0,   # Temperature must be positive
        #    lambda vars, res: vars["r0"] > 0,  # Radius must be positive
        #    lambda vars, res: vars["omega"] > 0  # Angular velocity must be positive
        ]

        super(Question16, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_central_pressure(r0, R, T, p0, v):
        """
        Calculate the central pressure at the center of a tornado given the parameters.

        Parameters:
        omega (float): Angular velocity (rad/s)
        r0 (float): Radius from the center (m)
        R (float): Specific gas constant for dry air (J/(kg*K))
        T (float): Temperature (K)
        p0 (float): Surface pressure at distance r0 (hPa)

        Returns:
        float: Central pressure (hPa)
        """
        omega = v / r0
        exponent = - (omega ** 2 * r0 ** 2) / (2 * R * T)
        central_pressure = p0 * math.exp(exponent)
        return Answer(central_pressure, "hPa", 1)


if __name__ == '__main__':
    q = Question16(unique_id="q")
    print(q.question())
    print(q.answer())