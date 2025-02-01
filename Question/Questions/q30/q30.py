import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question30(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """
Using the hydrostatic equation, derive an expression for the pressure at the center of a planet in terms of its surface gravity, radius {radius} and density {density}, assuming that the latter does not vary with depth. Insert values appropriate for the earth and evaluate the central pressure. 
[Hint: the gravity at radius {radius} is g(r) = G * m(r) / r^2 where m(r) is the mass inside a radius r and G = 6.67 * 10^-11 kg^-1 m^3 s^-2 is the gravitational constant. Assume the density of rock is {density} kg m^-3.]
        """

        self.func = self.calculate_central_pressure

        self.default_variables = {
            "surface_gravity": 9.81,  # Surface gravity (m/s^2)
            "radius": 6.37e6,         # Radius of the planet (m)
            "density": 2000           # Uniform density of the planet (kg/m^3)
        }

        self.constant = {
            # "gravitational_constant": 6.67e-11  # Gravitational constant (m^3 kg^-1 s^-2)
        }

        self.independent_variables = {
            "surface_gravity": {"min": 0.1, "max": 20.0, "granularity": 0.1},
            "radius": {"min": 1.0e6, "max": 1.0e7, "granularity": 1.0e5},
            "density": {"min": 1000, "max": 5000, "granularity": 10}
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = []

        super(Question30, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_central_pressure(surface_gravity, radius, density):
        """
        Calculate the central pressure at the center of a planet using the hydrostatic equation.

        Parameters:
            surface_gravity (float): Surface gravity (m/s^2)
            radius (float): Radius of the planet (m)
            density (float): Uniform density of the planet (kg/m^3)

        Returns:
            float: Central pressure at the center of the planet (Pa)
        """
        # Central pressure formula derived from the hydrostatic equation
        central_pressure = 0.5 * surface_gravity * density * radius
        return Answer(central_pressure, "Pa", 0)



if __name__ == '__main__':
    q = Question30(unique_id="q")
    print(q.question())
    print(q.answer())