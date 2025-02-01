import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question76(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """Somewhere (in a galaxy far, far away) there is a planet whose atmosphere is just like that of the Earth in all respects but one - it contains no moisture. The planet's troposphere is maintained by convection to be neutrally stable to vertical displacements. Its stratosphere is in radiative equilibrium, at a uniform temperature {stratospheric_temperature_C}°C, and temperature is continuous across the tropopause. If the surface pressure is {surface_pressure_hPa} hPa, and equatorial surface temperature is {surface_temperature_C}°C, what is the pressure at the equatorial tropopause?"""

        self.func = self.calculate_tropopause_pressure
        self.default_variables = {
            "surface_pressure_hPa": 1000,  # Surface pressure in hPa
            "surface_temperature_C": 32,  # Surface temperature in Celsius
            "stratospheric_temperature_C": -80,  # Stratospheric temperature in Celsius
        }

        self.constant = {
            "kappa": 2 / 7  # Ratio of specific heats for dry air
        }

        self.independent_variables = {
            "surface_pressure_hPa": {"min": 800, "max": 1100, "granularity": 1},
            "surface_temperature_C": {"min": -50, "max": 50, "granularity": 0.1},
            "stratospheric_temperature_C": {"min": -100, "max": -50, "granularity": 0.1},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: res > 0,  # Ensure the calculated pressure is positive
        ]

        super(Question76, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_tropopause_pressure(surface_pressure_hPa, surface_temperature_C, stratospheric_temperature_C, kappa=2 / 7):
        """
        Calculate the pressure at the tropopause for a planet with a dry atmosphere.

        Parameters:
        - surface_pressure_hPa (float): Surface pressure in hPa.
        - surface_temperature_C (float): Surface temperature in Celsius.
        - stratospheric_temperature_C (float): Temperature at the tropopause (and in the stratosphere) in Celsius.
        - kappa (float): Ratio of specific heats (default is 2/7 for dry air).

        Returns:
        - float: Pressure at the tropopause in hPa.
        """
        # Convert temperatures to Kelvin
        # surface_temperature_K = surface_temperature_C + 273.15
        # stratospheric_temperature_K = stratospheric_temperature_C + 273.15
        surface_temperature_K = surface_temperature_C + 273
        stratospheric_temperature_K = stratospheric_temperature_C + 273

        # Potential temperature is constant in the troposphere
        potential_temperature = surface_temperature_K

        # Calculate tropopause pressure
        tropopause_pressure_hPa = surface_pressure_hPa * (stratospheric_temperature_K / potential_temperature) ** (1 / kappa)
        return Answer(tropopause_pressure_hPa, "hPa", 1)


if __name__ == '__main__':
    q = Question76(unique_id="q")
    print(q.question())
    print(q.answer())