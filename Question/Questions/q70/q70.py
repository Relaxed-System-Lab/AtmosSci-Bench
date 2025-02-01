import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question70(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
12.2. Find the Rossby critical velocities for zonal wave numbers 1, 2, and 3 (i.e., for these wavelengths around a latitude circle). 
Let the motion be referred to a $\\beta$-plane centered at {latitude}°, scale height $H={H}$ km, 
buoyancy frequency $N={N}$ s⁻¹, and infinite meridional scale $(l=0)$.
        """
        self.func = self.calculate_critical_velocity
        self.default_variables = {
            "s1": 1,                # Zonal wave number 1
            "s2": 2,                # Zonal wave number 2
            "s3": 3,                # Zonal wave number 3
            "H": 7.0,               # Scale height (km)
            "N": 2e-2,              # Buoyancy frequency (s^-1)
            "latitude": 45,         # Latitude (degrees)
        }

        self.constant = {
            "Omega": 7.2921e-5,     # Earth's rotation rate (s^-1)
            "a": 6.371e6            # Earth's radius (m)
        }

        self.independent_variables = {
            "s1": {"min": 1, "max": 3, "granularity": 1},
            "latitude": {"min": 0, "max": 90, "granularity": 1},
            "H": {"min": 1, "max": 20, "granularity": 0.1},
            "N": {"min": 0.01, "max": 0.1, "granularity": 0.001},
        }

        self.dependent_variables = {
            "s2": lambda vars: vars["s1"] + np.random.randint(1, 3),  # Zonal wave number 2
            "s3": lambda vars: vars["s2"] + np.random.randint(1, 3),  # Zonal wave number 3
        }

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["latitude"] > 0,  # Latitude must be positive
        ]
        super(Question70, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_critical_velocity(s1, s2, s3, H, N, latitude, Omega, a):
        """
        Calculate Rossby critical velocities for three given zonal wave numbers.

        Parameters:
            s1, s2, s3 (int): Zonal wave numbers (e.g., 1, 2, 3).
            H (float): Scale height in km.
            N (float): Buoyancy frequency in s^-1.
            latitude (float): Latitude in degrees.
            Omega (float): Earth's rotation rate in s^-1.
            a (float): Earth's radius in meters.

        Returns:
            dict: Critical velocities for the three zonal wave numbers.
        """
        beta = 2 * Omega * np.cos(np.radians(latitude)) / a  # Calculate beta
        f0 = 2 * Omega * np.sin(np.radians(latitude))  # Coriolis parameter

        # Convert H from km to m for calculation
        H_m = H * 1e3

        k_squared_constant = f0**2 / (4 * N**2 * H_m**2)  # Constant term for k^2

        def compute_U_c(s):
            k = s / (a * np.cos(np.radians(latitude)))  # Zonal wave number in rad/m
            k_squared = k**2 + k_squared_constant
            return beta / k_squared

        # Calculate for each s
        U_c1 = compute_U_c(s1)
        U_c2 = compute_U_c(s2)
        U_c3 = compute_U_c(s3)

        return NestedAnswer({
            "s1": Answer(U_c1, "m/s", 1),
            "s2": Answer(U_c2, "m/s", 1),
            "s3": Answer(U_c3, "m/s", 1)
        })



if __name__ == '__main__':
    q = Question70(unique_id="q")
    print(q.question())
    print(q.answer())