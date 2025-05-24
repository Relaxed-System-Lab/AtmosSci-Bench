import random, math
from question import Question
from answer import Answer, NestedAnswer


class Question60(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """Assume the lapse rate at the 850 hPa level is 4 K km^-1. Given that the temperature at a specific location is dropping at a rate of {temp_change_rate} K h^-1, with a westerly wind blowing at {wind_speed} m s^-1, and the temperature declines towards the west at {temp_gradient_x} K per 100 km, determine the vertical velocity at the 850 hPa level using the adiabatic method."""
        self.func = self.calculate_vertical_velocity

        self.default_variables = {
            "lapse_rate": 4.0,                # Lapse rate (Gamma) in K/km
            "temp_change_rate": -2.0,         # Temperature change rate in K/h
            "wind_speed": 10.0,               # Westerly wind speed in m/s
            "temp_gradient_x": 5.0            # Temperature gradient in K per 100 km
        }

        self.constant = {
            "lapse_rate_dry": 9.8 * 1e-3            # Dry adiabatic lapse rate in K/km
        }

        self.independent_variables = {
            "lapse_rate": {"min": 1.0, "max": 10.0, "granularity": 0.1},
            "temp_change_rate": {"min": -10.0, "max": -1.0, "granularity": 0.1},
            "wind_speed": {"min": 0.0, "max": 50.0, "granularity": 0.1},
            "temp_gradient_x": {"min": 1.0, "max": 10.0, "granularity": 0.1}
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["lapse_rate"] > 0
        ]

        self.knowledge = """
Application of (3.40) to infer the vertical velocity field requires knowledge of the horizontal divergence. To determine the horizontal divergence, the partial derivatives $\partial u / \partial x$ and $\partial v / \partial y$ are generally estimated from the fields of $u$ and $v$ by using finite difference approximations (see Section 13.2.1). For example, to determine the divergence of the horizontal velocity at the point $x_{0}, y_{0}$ in Figure 3.10, we write

$$
\begin{equation*}
\frac{\partial u}{\partial x}+\frac{\partial v}{\partial y} \approx \frac{u\left(x_{0}+d\right)-u\left(x_{0}-d\right)}{2 d}+\frac{v\left(y_{0}+d\right)-v\left(y_{0}-d\right)}{2 d} \tag{3.41}
\end{equation*}
$$
"""

        super(Question60, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_vertical_velocity(lapse_rate, temp_change_rate, wind_speed, temp_gradient_x, lapse_rate_dry = 9.8 * 1e-3):
        """
        Computes the vertical velocity at a given pressure level using the adiabatic method.

        Parameters:
            lapse_rate (float): Lapse rate (Gamma) at the given pressure level in K/km.
            temp_change_rate (float): Temperature change rate in K/h.
            wind_speed (float): Wind speed in m/s.
            temp_gradient_x (float): Temperature gradient in the x-direction (K per 100 km).

        Returns:
            float: Vertical velocity (w) in m/s.
        """
        # Convert lapse rate to K/m
        lapse_rate = lapse_rate * 1e-3

        # Convert temperature change rate to K/s
        temp_change_rate = temp_change_rate / 3600

        # Convert temperature gradient from K/100 km to K/m
        temp_gradient_x = temp_gradient_x / 1e5

        # Calculate S_p
        S_p = lapse_rate_dry - lapse_rate

        # Calculate the term inside the brackets
        temp_tendency = temp_change_rate + wind_speed * temp_gradient_x

        # Calculate vertical velocity (w)
        w = -temp_tendency / S_p

        # Convert w to cm/s
        w_in_cm = w * 100
        return Answer(w_in_cm, "cm/s", 2)



if __name__ == '__main__':
    q = Question60(unique_id="q")
    print(q.question())
    print(q.answer())