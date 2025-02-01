import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question74(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
Estimate the TEM residual vertical velocity in the westerly shear zone of the equatorial QBO assuming that radiative cooling can be approximated by Newtonian cooling with a {relaxation_time}-day relaxation time, the vertical shear is {vertical_shear} m/s per 5 km, and the meridional half-width is {meridional_half_width}° latitude.
        """
        self.func = self.calculate_residual_velocity

        self.default_variables = {
            "relaxation_time": 20,  # Relaxation time in days
            "vertical_shear": 20,  # Vertical shear in m/s per 5 km
            "meridional_half_width": 12,  # Meridional half-width in degrees latitude
            # "theta_gradient": 0.005,  # Typical value for ∂θ/∂z (K/m)
            # "theta_mean": 300,  # Mean potential temperature (K)
        }

        self.constant = {
            "gravity": 9.81,  # Gravity acceleration (m/s^2)
            "earth_rotation_rate": 7.292e-5,  # Earth's rotation rate (rad/s)
            "earth_radius": 6.371e6,  # Earth's radius (m)
        }

        self.independent_variables = {
            "relaxation_time": {"min": 10, "max": 30, "granularity": 1},  # Days
            "vertical_shear": {"min": 10, "max": 50, "granularity": 1},  # m/s per 5 km
            "meridional_half_width": {"min": 5, "max": 20, "granularity": 1},  # Degrees
            # "theta_gradient": {"min": 0.001, "max": 0.01, "granularity": 0.001},  # K/m
            # "theta_mean": {"min": 250, "max": 350, "granularity": 10},  # K
        }

        self.dependent_variables = {
            # "alpha": lambda vars: 1 / (vars["relaxation_time"] * 86400),  # s^-1
            # "beta": lambda vars: 2 * self.constant["earth_rotation_rate"] / self.constant["earth_radius"],  # m^-1 s^-1
            # "Lambda": lambda vars: vars["vertical_shear"] / 5000,  # s^-1
            # "L": lambda vars: self.constant["earth_radius"] * (vars["meridional_half_width"] * math.pi / 180),  # m
            # "N_squared": lambda vars: (self.constant["gravity"] / vars["theta_mean"]) * vars["theta_gradient"],  # s^-2
        }

        self.choice_variables = {
        }

        self.custom_constraints = [
            lambda vars, res: vars["relaxation_time"] > 0,  # Relaxation time must be positive
            lambda vars, res: vars["vertical_shear"] > 0,  # Vertical shear must be positive
            lambda vars, res: vars["meridional_half_width"] > 0,  # Meridional half-width must be positive
            # lambda vars, res: vars["theta_mean"] > 0,  # Potential temperature must be positive
            lambda vars, res: res < 0,  # Residual velocity must indicate subsidence (negative)
        ]



        super(Question74, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_residual_velocity(relaxation_time, vertical_shear, meridional_half_width, gravity, earth_rotation_rate, earth_radius):
        """
        Calculate the TEM residual vertical velocity.

        Parameters:
        relaxation_time (float): Relaxation time in days
        vertical_shear (float): Vertical shear (m/s per 5 km)
        meridional_half_width (float): Meridional half-width (degrees latitude)
        theta_gradient (float): Potential temperature gradient (K/m)
        theta_mean (float): Mean potential temperature (K)
        gravity (float): Gravitational acceleration (m/s^2)
        earth_rotation_rate (float): Earth's rotation rate (rad/s)
        earth_radius (float): Earth's radius (m)

        Returns:
        tuple: Residual vertical velocity in m/s and m/day
        """
        # Convert relaxation time to alpha
        alpha = 1 / (relaxation_time * 86400)  # Convert days to seconds
        
        # Calculate beta
        beta = 2 * earth_rotation_rate / earth_radius
        
        # Calculate Lambda (shear rate)
        Lambda = vertical_shear / 5000  # 5000 m = 5 km
        
        # Calculate L (meridional half-width in meters)
        L = earth_radius * (meridional_half_width * math.pi / 180)

        # Calculate N^2 (static stability)
        N_squared = 0.0004

        # Coefficient in the equation
        coefficient = (5 / 6) * alpha * beta * Lambda * (L ** 2) / N_squared

        # Residual vertical velocity in m/s
        w_star_m_per_s = -coefficient

        # Convert to m/day
        w_star_m_per_day = w_star_m_per_s * 86400  # 86400 seconds in a day

        return Answer(w_star_m_per_day, "m/day", 2)


if __name__ == '__main__':
    q = Question74(unique_id="q")
    print(q.question())
    print(q.answer())