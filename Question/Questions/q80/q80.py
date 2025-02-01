import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question80(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """ 
Spectroscopic measurements show that a mass of water vapor of more than {critical_mass} kg/m^2 in a column of atmosphere is opaque to the 'terrestrial' waveband. Given that water vapor typically has a density of {rho_v_surface} kg/m^3 at sea level and decays in the vertical like e^(-z/{b}), where z is the height above the surface and b ∼ {b} km, estimate at what height the atmosphere becomes transparent to terrestrial radiation.
        """

        self.func = self.calculate_transparency_height
        self.default_variables = {
            
            "b": 3.0,  # Scale height (km)
        }

        self.constant = {
                "rho_v_surface": 1e-2,  # Surface density of water vapor (kg/m^3)
                "critical_mass": 3.0,  # Critical mass of water vapor per square meter (kg/m^2)

        }

        self.independent_variables = {
            "rho_v_surface": {"min": 0.001, "max": 0.1, "granularity": 0.001},
            "b": {"min": 2.0, "max": 4.0, "granularity": 0.1},
            "critical_mass": {"min": 1.0, "max": 10.0, "granularity": 0.1},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: res > 0  # Ensure the calculated height is positive
        ]

        super(Question80, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_transparency_height(rho_v_surface, b, critical_mass):
        """
        Calculate the height (z*) at which the atmosphere becomes transparent
        to terrestrial radiation.

        Parameters:
            rho_v_surface (float): Surface density of water vapor (kg/m^3).
            b (float): Scale height of water vapor (km).
            critical_mass (float): Critical mass of water vapor per square meter (kg/m^2).

        Returns:
            float: The height (z*) at which the atmosphere becomes transparent (in kilometers).
        """
        # Calculate the height at which the atmosphere becomes transparent
        b_meters = b * 1000  # Convert scale height from km to m
        z_star = -b_meters * math.log(critical_mass / (b_meters * rho_v_surface))

        z_star_in_km = z_star / 1000
        return Answer(z_star_in_km, "km", 2)


if __name__ == '__main__':
    q = Question80(unique_id="q")
    print(q.question())
    print(q.answer())