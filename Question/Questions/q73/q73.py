import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question73(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """ 
For a Rossby-gravity wave of zonal wave number {zonal_wave_number} and phase speed {phase_speed} m/s, determine the latitude at which the vertical momentum flux M ≡ \rho_0 \overline{{u' w'}} is a maximum.
        """
        self.func = self.calculate_max_latitude
        self.default_variables = {
            "phase_speed": -20,  # Phase speed c in m/s
            "zonal_wave_number": 4,  # Zonal wave number k
            "earth_radius": 6.37e6,  # Earth's radius in meters
            "beta": 1.458e-4,  # Beta parameter (s^-1 m^-1)
            "omega": 7.292e-5,  # Earth's angular velocity (rad/s)
        }
        self.constant = {
        }
        self.independent_variables = {
            "phase_speed": {"min": -100, "max": 100, "granularity": 1},
            "zonal_wave_number": {"min": 1, "max": 10, "granularity": 1},
        }
        self.dependent_variables = {
            "earth_radius": lambda vars: 6.37e6,  # Constant Earth radius
            "beta": lambda vars: 1.458e-4,  # Constant beta parameter
            "omega": lambda vars: 7.292e-5,  # Constant angular velocity
        }
        self.choice_variables = {
            "wave_properties": [
                {"zonal_wave_number": 2, "phase_speed": -10},
                {"zonal_wave_number": 4, "phase_speed": -20},
                {"zonal_wave_number": 6, "phase_speed": -30},
            ]
        }
        self.custom_constraints = [
            lambda vars, res: vars["phase_speed"] < 0,  # Phase speed must be negative
        ]

        super(Question73, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_max_latitude(phase_speed, zonal_wave_number, earth_radius, beta, omega):
        """
        Calculates the latitude where the vertical momentum flux is maximized for a Rossby-gravity wave.

        Parameters:
        phase_speed (float): Phase speed of the wave (c) in m/s.
        zonal_wave_number (int): Zonal wave number (k), unitless.
        earth_radius (float): Earth's radius in meters.
        beta (float): Beta parameter (∂f/∂y) in s^-1 m^-1.
        omega (float): Earth's angular velocity in rad/s.

        Returns:
        tuple: (y_max_km, latitude_deg), where y_max_km is the distance in km
               and latitude_deg is the latitude in degrees.
        """
        # Compute the meridional wavenumber v = c * k / a
        v = phase_speed * zonal_wave_number / earth_radius

        # Compute the y_max in meters
        denominator = 1 + (0.5 * v / omega)
        y_max_m = phase_speed * zonal_wave_number / (2 * omega * math.sqrt(denominator))
        
        # Convert y_max to km
        y_max_km = y_max_m / 1000

        # Convert y_max to degrees latitude
        latitude_deg = y_max_km / (earth_radius * (math.pi / 180) / 1000)

        return y_max_km, latitude_deg



if __name__ == '__main__':
    q = Question73(unique_id="q")
    print(q.question())
    print(q.answer())