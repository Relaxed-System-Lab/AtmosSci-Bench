import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question71(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """ 
Find the geopotential and vertical velocity fluctuations for a Kelvin wave of 
zonal wave number {s}, phase speed {c} m/s, and zonal velocity perturbation amplitude 
{u_prime} m/s. Let N^2 = {N_squared} s^-2.
        """
        self.func = self.calculate_fluctuations

        self.default_variables = {
            "u_prime": 5.0,  # Zonal velocity perturbation amplitude (m/s)
            "c": 40.0,       # Phase speed (m/s)
            "N_squared": 4e-4,  # Brunt-Väisälä frequency squared (s^-2)
            "s": 1.0         # Planetary wave number
        }

        self.constant = {
            "planet_radius": 6.37e6  # Planetary radius (m)
        }

        self.independent_variables = {
            "u_prime": {"min": 1.0, "max": 20.0, "granularity": 0.1},
            "c": {"min": 10.0, "max": 100.0, "granularity": 1.0},
            "N_squared": {"min": 1e-4, "max": 1e-3, "granularity": 1e-5},
            "s": {"min": 1, "max": 10, "granularity": 1},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["c"] > 0,
            lambda vars, res: vars["N_squared"] > 0,
        ]


        super(Question71, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_fluctuations(u_prime, c, N_squared, s, planet_radius):
        """
        Calculate the geopotential and vertical velocity fluctuations for a Kelvin wave.

        Parameters:
            u_prime (float): Zonal velocity perturbation amplitude (m/s).
            c (float): Phase speed (m/s).
            N_squared (float): Brunt-Väisälä frequency squared (s^-2).
            s (int): Planetary wave number.
            planet_radius (float): Planetary radius (m).

        Returns:
            tuple: (Geopotential fluctuation (Phi'), Vertical velocity fluctuation (w')).
        """
        # Geopotential fluctuation
        phi_prime = u_prime * c

        # Vertical velocity fluctuation
        k = s / planet_radius  # Zonal wave number
        m_squared = (N_squared / c**2)
        m = math.sqrt(m_squared)
        w_prime = (c * k * m / N_squared) * phi_prime

        return NestedAnswer({
            "Geopotential fluctuation": Answer(phi_prime, "m^2/s^2", 6),
            "Vertical velocity fluctuation": Answer(w_prime, "m/s", 5)
        })


if __name__ == '__main__':
    q = Question71(unique_id="q")
    print(q.question())
    print(q.answer())