import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question68(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Geophysics"
        self.template = """Examine a thermally stratified fluid within a rotating annulus, which has an inner radius of {inner_radius} m, an outer radius of {outer_radius} m, and a depth of {depth} m. The temperature at the bottom boundary is maintained at {{T0}}. The fluid obeys the equation of state (10.75) with $\rho_0={rho0}$ kg/m\(^3\) and $\epsilon={epsilon}$ K\(^{-1}\). If the temperature increases linearly with height at the outer radial boundary at a rate of {temp_gradient} °C/cm and remains constant with height at the inner radial boundary, calculate the geostrophic velocity at the upper boundary for a rotation rate of {omega} rad/s. (Assume a linear temperature dependency on radius at each level.)"""
        self.func = self.calculate_geostrophic_velocity

        self.default_variables = {
            "rho0": 1000.0,          # Reference density (kg/m^3)
            "epsilon": 2e-4,          # Thermal expansion coefficient (K^-1)
            "omega": 1.0,            # Angular velocity of rotation (rad/s)
            "inner_radius": 0.8,     # Inner radius (m)
            "outer_radius": 1.0,     # Outer radius (m)
            "depth": 0.1,            # Depth of fluid (m)
            "temp_gradient": 1.0     # Temperature gradient along outer wall (°C/cm)
        }

        self.constant = {
            "g": 9.8,                # Gravitational acceleration (m/s^2)
        }

        self.independent_variables = {
            "rho0": {"min": 500.0, "max": 2000.0, "granularity": 10.0},
            "epsilon": {"min": 1e-5, "max": 5e-4, "granularity": 1e-5},
            "omega": {"min": 0.1, "max": 5.0, "granularity": 0.1},
            "inner_radius": {"min": 0.5, "max": 1.0, "granularity": 0.1},
            "outer_radius": {"min": 1.0, "max": 1.5, "granularity": 0.1},
            "depth": {"min": 0.05, "max": 0.5, "granularity": 0.01},
            "temp_gradient": {"min": 0.1, "max": 5.0, "granularity": 0.1}
        }

        self.dependent_variables = {
            "g": lambda vars: 9.8  # Gravitational acceleration is constant on Earth's surface
        }

        self.choice_variables = {
        }

        self.custom_constraints = [
            lambda vars, res: vars["inner_radius"] < vars["outer_radius"],  # Ensure physical dimensions are valid
        ]
        super(Question68, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_geostrophic_velocity(epsilon, g, omega, inner_radius, outer_radius, depth, temp_gradient, rho0):
        """
        Calculate the geostrophic velocity at the upper boundary.

        Args:
            epsilon (float): Thermal expansion coefficient (K^-1).
            g (float): Gravitational acceleration (m/s^2).
            omega (float): Angular velocity of rotation (rad/s).
            inner_radius (float): Inner radius (m).
            outer_radius (float): Outer radius (m).
            depth (float): Depth of fluid (m).
            temp_gradient (float): Temperature gradient along outer wall (°C/cm).

        Returns:
            float: Geostrophic velocity at the upper boundary (m/s).
        """
        # Convert temperature gradient from °C/cm to °C/m
        temp_gradient_m = temp_gradient * 100

        # Calculate L, the radial width of the annulus
        L = outer_radius - inner_radius

        # Apply the geostrophic velocity formula
        velocity = (epsilon * g) / (2 * omega * L) * temp_gradient_m * (depth**2) / 2
        return velocity



if __name__ == '__main__':
    q = Question68(unique_id="q")
    print(q.question())
    print(q.answer())