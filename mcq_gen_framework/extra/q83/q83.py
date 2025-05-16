import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question83(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Geophysics"
        self.template = self.template = """Calculate the proportion of centrifugal acceleration to gravitational acceleration at a latitude of {latitude_deg}° on {planet_name}."""

        self.func = self.calculate_ratio

        self.default_variables = {
            "omega": 7.292115e-5,        # rad/s
            "radius": 6371000,           # m
            "latitude_deg": 0,           # degrees (equator)
            "g_equator": 9.7803253359,   # m/s²
            "k": 0.00193185265241,
            "e_sq": 0.00669437999014,
            "planet_name": "Earth"
        }

        self.constant = {}

        self.independent_variables = {
            "omega": {"min": 1e-5, "max": 1e-3, "granularity": 1e-6},
            "radius": {"min": 1e6, "max": 1e8, "granularity": 1e3},
            "latitude_deg": {"min": 0, "max": 90, "granularity": 0.1}
        }

        self.dependent_variables = {
            "g_equator": lambda vars: 6.67430e-11 * 5.972e24 / (vars["radius"] ** 2)  # Simplified for general planetary gravity
        }

        self.choice_variables = {
            "planet": [
                {"planet_name": "Earth", "omega": 7.292115e-5, "radius": 6371000, "g_equator": 9.7803253359, "k": 0.00193185265241, "e_sq": 0.00669437999014},
                {"planet_name": "Mars", "omega": 7.088218e-5, "radius": 3396200, "g_equator": 3.72076, "k": 0.005, "e_sq": 0.00589},
                {"planet_name": "Jupiter", "omega": 1.7585e-4, "radius": 71492000, "g_equator": 24.79, "k": 0.06487, "e_sq": 0.06487},
                {"planet_name": "Venus", "omega": -2.992e-7, "radius": 6051800, "g_equator": 8.87, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Mercury", "omega": 1.240e-6, "radius": 2439700, "g_equator": 3.7, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Saturn", "omega": 1.654e-4, "radius": 60268000, "g_equator": 10.44, "k": 0.09796, "e_sq": 0.09796},
                {"planet_name": "Uranus", "omega": -1.012e-4, "radius": 25559000, "g_equator": 8.69, "k": 0.0229, "e_sq": 0.0229},
                {"planet_name": "Neptune", "omega": 1.083e-4, "radius": 24764000, "g_equator": 11.15, "k": 0.0171, "e_sq": 0.0171},
                {"planet_name": "Moon", "omega": 2.6617e-6, "radius": 1737100, "g_equator": 1.62, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Io", "omega": 4.112e-5, "radius": 1821500, "g_equator": 1.796, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Europa", "omega": 2.048e-5, "radius": 1560800, "g_equator": 1.314, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Ganymede", "omega": 1.017e-5, "radius": 2634100, "g_equator": 1.428, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Callisto", "omega": 4.235e-6, "radius": 2410300, "g_equator": 1.235, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Titan", "omega": 4.560e-6, "radius": 2575500, "g_equator": 1.352, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Enceladus", "omega": 5.307e-5, "radius": 252100, "g_equator": 0.113, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Triton", "omega": -1.237e-5, "radius": 1353400, "g_equator": 0.779, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Pluto", "omega": -1.138e-5, "radius": 1188300, "g_equator": 0.62, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Ceres", "omega": 1.923e-4, "radius": 473000, "g_equator": 0.27, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Haumea", "omega": 4.5e-4, "radius": 816000, "g_equator": 0.44, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Makemake", "omega": 1.3e-4, "radius": 715000, "g_equator": 0.5, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Eris", "omega": 8.0e-6, "radius": 1163000, "g_equator": 0.82, "k": 0.000, "e_sq": 0.000},
                {"planet_name": "Sun", "omega": 2.9e-6, "radius": 696340000, "g_equator": 274.0, "k": 0.0, "e_sq": 0.0},
                {"planet_name": "Proxima Centauri b", "omega": 5.0e-5, "radius": 7160000, "g_equator": 10.8, "k": 0.002, "e_sq": 0.005},
                {"planet_name": "Kepler-452b", "omega": 4.5e-5, "radius": 10000000, "g_equator": 19.6, "k": 0.003, "e_sq": 0.006},
                {"planet_name": "Gliese 581g", "omega": 3.5e-5, "radius": 9000000, "g_equator": 16.4, "k": 0.003, "e_sq": 0.006},
                {"planet_name": "HD 209458 b", "omega": 2.0e-4, "radius": 94400000, "g_equator": 9.28, "k": 0.050, "e_sq": 0.050},
                {"planet_name": "WASP-12b", "omega": 1.7e-4, "radius": 112000000, "g_equator": 9.0, "k": 0.040, "e_sq": 0.040},
                {"planet_name": "55 Cancri e", "omega": 9.0e-5, "radius": 10100000, "g_equator": 18.0, "k": 0.004, "e_sq": 0.007},
                {"planet_name": "TRAPPIST-1e", "omega": 6.0e-5, "radius": 5810000, "g_equator": 9.1, "k": 0.0015, "e_sq": 0.003},
                {"planet_name": "K2-18b", "omega": 4.8e-5, "radius": 12700000, "g_equator": 11.4, "k": 0.0035, "e_sq": 0.007}
            ]
        }

        self.custom_constraints = [
            lambda vars, res: res > 0 and res < 0.1  # ratio is small but positive
        ]

        super(Question83, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_ratio(omega, radius, latitude_deg, g_equator, k, e_sq, planet_name):
        """
        Calculate the ratio of centrifugal acceleration to gravitational acceleration
        at the equator (or given latitude) of a rotating planet.
        """
        import math

        # Convert latitude to radians
        phi = math.radians(latitude_deg)

        # Centrifugal acceleration
        g_centrifugal = omega**2 * radius * math.cos(phi)

        # Gravitational acceleration using a latitude-dependent model
        g_gravity = g_equator * (1 + k * math.sin(phi)**2) / math.sqrt(1 - e_sq * math.sin(phi)**2)

        # Ratio
        ratio = g_centrifugal / g_gravity

        return Answer(ratio, "", 6)

if __name__ == '__main__':
    q = Question83(unique_id="q")
    print(q.question())
    print(q.answer())