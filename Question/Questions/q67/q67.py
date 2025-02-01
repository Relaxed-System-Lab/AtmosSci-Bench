import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question67(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """10.8. Compute the surface torque per unit horizontal area exerted on the atmosphere by topography for the following distribution of surface pressure and surface height:

p_{{s}}=p_{{0}}+\hat{{p}} \sin k x, \quad h=\hat{{h}} \sin (k x-\gamma)

where p_{{0}}={p0} hPa, \hat{{p}}={p_hat} hPa, \hat{{h}}={h_hat} m, \gamma={gamma} rad, and k=1 /(a \cos \phi). Here, \phi={phi} radians is the latitude, and a is the radius of the earth. Express the answer in \mathrm{{kg}} \mathrm{{s}}^{{-2}}.
"""
        self.func = self.calculate_surface_torque
        self.default_variables = {
            "phi": 0.7854,  # Latitude in radians (pi/4)
            "gamma": 0.5236,  # Phase offset in radians (pi/6)
            "p0": 1000,  # Mean surface pressure in hPa
            "p_hat": 10,  # Amplitude of pressure perturbation in hPa
            "h_hat": 2500  # Amplitude of surface height perturbation in meters
        }

        self.constant = {
            "a": 6371e3,  # Radius of Earth in meters
        }

        self.independent_variables = {
            "p_hat": {"min": 1, "max": 20, "granularity": 0.1},
            "h_hat": {"min": 100, "max": 5000, "granularity": 10},
            "phi": {"min": 0, "max": 1.57, "granularity": 0.01},
            "gamma": {"min": 0, "max": 6.28, "granularity": 0.01},
            "p0": {"min": 900, "max": 1100, "granularity": 10},
        }

        self.dependent_variables = {
            # "k": lambda vars: 1 / (self.constant["a"] * np.cos(vars["phi"])),
        }

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["p_hat"] > 0 and vars["h_hat"] > 0
        ]
        super(Question67, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_surface_torque(a, phi, gamma, p0, p_hat, h_hat):
        """
        Compute the surface torque per unit horizontal area exerted on the atmosphere by topography.

        Parameters:
            a (float): Radius of the Earth (m).
            phi (float): Latitude (radians).
            gamma (float): Phase offset (radians).
            p0 (float): Mean surface pressure (hPa).
            p_hat (float): Amplitude of pressure perturbation (hPa).
            h_hat (float): Amplitude of surface height perturbation (m).

        Returns:
            float: Surface torque per unit horizontal area (kg s^-2).
        """
        # Compute the wavenumber k
        k = 1 / (a * np.cos(phi))

        # Compute the torque using the given formula
        p_hat = p_hat * 100  # Convert hPa to Pa
        torque = -(p_hat * h_hat / 2) * np.sin(gamma)

        return Answer(torque, "kg/s^2", 0)



if __name__ == '__main__':
    q = Question67(unique_id="q")
    print(q.question())
    print(q.answer())