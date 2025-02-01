import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question72(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
(a) Find the geopotential and vertical velocity fluctuations for a Kelvin wave of 
zonal wave number {s}, phase speed {c} m/s, and zonal velocity perturbation amplitude 
{u_prime} m/s. Let N^2 = {N_squared} s^-2.

(b) For the situation of Problem (a), compute the vertical momentum flux 
M ≡ \rho_0 \overline{{u' w'}}. Show that M is constant with height.
        """
        self.func = self.calculate_fluctuations

        self.default_variables = {
            "u_prime": 5.0,       # Zonal velocity perturbation amplitude (m/s)
            "c": 40.0,            # Phase speed (m/s)
            "N_squared": 4e-4,    # Brunt-Väisälä frequency squared (s^-2)
            "s": 1.0,             # Planetary wave number
        }

        self.constant = {
            "planet_radius": 6.37e6,  # Planetary radius (m)
            "rho_s": 1.0          # Reference density (kg/m^3)
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

        super(Question72, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_fluctuations(u_prime, c, N_squared, s, rho_s, planet_radius):
        """
        Calculate the geopotential and vertical velocity fluctuations, and vertical momentum flux.

        Parameters:
            u_prime (float): Zonal velocity perturbation amplitude (m/s).
            c (float): Phase speed (m/s).
            N_squared (float): Brunt-Väisälä frequency squared (s^-2).
            s (int): Planetary wave number.
            rho_s (float): Reference density (kg/m^3).
            planet_radius (float): Planetary radius (m).

        Returns:
            tuple: 
                - Geopotential fluctuation (Phi', m^2/s^2)
                - Vertical velocity fluctuation (w', m/s)
                - Vertical momentum flux (M, kg/m/s^2)
        """
        # (a) Geopotential fluctuation
        phi_prime = u_prime * c

        # Vertical velocity fluctuation
        k = s / planet_radius  # Zonal wave number
        m_squared = (N_squared / c**2)
        m = math.sqrt(m_squared)
        w_prime = (c * k * m / N_squared) * phi_prime

        # (b) Vertical momentum flux
        momentum_flux = rho_s * (u_prime**2 * c**2 * k * m / N_squared) * 0.5

        return NestedAnswer({
            "(a)": NestedAnswer({
                "Geopotential fluctuation": Answer(phi_prime, "m^2/s^2", 6),
                "Vertical velocity fluctuation": Answer(w_prime, "m/s", 5)
            }),
            "(b)": NestedAnswer({
                "Vertical momentum flux": Answer(momentum_flux, "kg/m/s", 5)
            })
        })
        # return phi_prime, w_prime, momentum_flux



if __name__ == '__main__':
    q = Question72(unique_id="q")
    print(q.question())
    print(q.answer())