import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question44(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """ 
For the conditions of Problem 1.14, compute the variation of the temperature with respect to height. 
(This is referred to as an autoconvective lapse rate.)
        """
        self.func = self.calculate_lapse_rate
        self.default_variables = {
            "surface_pressure": 101325,  # Surface pressure (p0) in Pa
            "surface_density": 1.225,    # Surface density (rho0) in kg/m^3
        }

        self.constant = {
            "gas_constant": 287.05       # Specific gas constant (R) in J/(kg·K)
        }

        self.independent_variables = {
            "surface_pressure": {"min": 90000, "max": 120000, "granularity": 100},
            "surface_density": {"min": 1.0, "max": 1.5, "granularity": 0.01},
        }

        self.dependent_variables = {}

        self.choice_variables = {
        }

        self.custom_constraints = [
            lambda vars, res: vars["surface_pressure"] > 0,
            lambda vars, res: vars["surface_density"] > 0
        ]

        super(Question44, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_lapse_rate(surface_pressure, surface_density, gas_constant):
        """
        Computes the autoconvective lapse rate (Gamma) and temperature variation function.

        Parameters:
            surface_pressure (float): Surface pressure (p0) in Pascals.
            surface_density (float): Surface density (rho0) in kg/m^3.
            gas_constant (float): Specific gas constant (R) in J/(kg·K).

        Returns:
            dict: 
                - "lapse_rate": Temperature gradient (Gamma) in K/km.
                - "temperature_variation": Function for temperature variation with height.
        """
        # Constants
        gravity = 9.81  # Gravitational acceleration in m/s^2

        # Calculate lapse rate
        lapse_rate = gravity / gas_constant * 1000  # Convert to K/km

        # Temperature variation function
        def temperature_variation(height, surface_temperature):
            return surface_temperature - (gravity / gas_constant) * height

        return {
            "lapse_rate": lapse_rate,
            "temperature_variation": temperature_variation
        }



if __name__ == '__main__':
    q = Question44(unique_id="q")
    print(q.question())
    print(q.answer())