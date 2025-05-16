import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question90(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Physical Oceanography"
        self.template = """A vessel is navigating an area where deep water waves have a wavelength of {wavelength_m} meters. Considering the vessel's speed is {vessel_speed_m_s} m s⁻¹, determine the ship's speed using the Froude number."""
        self.func = self.calculate_froude_number

        self.default_variables = {
            "vessel_speed_m_s": 5.0,  # Speed of the vessel in meters per second
            "wavelength_m": 100.0     # Wavelength in meters
        }

        self.constant = {
            # "gravity_m_s2": 9.8       # Gravitational acceleration (m/s²)
        }

        self.independent_variables = {
            "vessel_speed_m_s": {"min": 0.1, "max": 20.0, "granularity": 0.1},
            "wavelength_m": {"min": 1.0, "max": 1000.0, "granularity": 1.0}
        }

        self.dependent_variables = {
            # No dependent variables needed; output is derived from the independent variables
        }

        self.choice_variables = {
            # No grouped choices needed for this question
        }

        self.custom_constraints = [
            lambda vars, res: res > 0  # Froude number must be positive
        ]

        super(Question90, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_froude_number(vessel_speed_m_s, wavelength_m):
        """
        Calculates the Froude number using the formula:
        Fr = U / sqrt(L * g)
        
        Parameters:
        - vessel_speed_m_s: Vessel speed (m/s)
        - wavelength_m: Wavelength (m)

        Returns:
        - Froude number (dimensionless)
        """
        gravity_m_s2 = 9.8  # Acceleration due to gravity (constant)
        froude_number = vessel_speed_m_s / (wavelength_m * gravity_m_s2) ** 0.5
        return Answer(froude_number, "", 4)


if __name__ == '__main__':
    q = Question90(unique_id="q")
    print(q.question())
    print(q.answer())