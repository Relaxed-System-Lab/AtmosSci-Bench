import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question92(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """The polar ice caps, which cover an area of {area_km2} km^2, are thought to hold a total equivalent volume of {volume_km3} km^3 of liquid water. With the average yearly precipitation over these ice caps estimated at {precip_in_per_year} inches, calculate the residence time of water in the polar ice caps, assuming the volume does not change over time."""

        self.func = self.calculate_residence_time

        self.default_variables = {
            "volume_km3": 2.4e7,
            "area_km2": 1.6e7,
            "precip_in_per_year": 5.0
        }

        self.constant = {
        }

        self.independent_variables = {
            "volume_km3": {"min": 1e6, "max": 5e7, "granularity": 1e6},
            "area_km2": {"min": 1e6, "max": 2e7, "granularity": 1e6},
            "precip_in_per_year": {"min": 1.0, "max": 20.0, "granularity": 0.1}
        }

        self.dependent_variables = {
            # No dependent variables in this case
        }

        self.choice_variables = {
            # No categorical choice variables in this case
        }

        self.custom_constraints = [
            lambda vars, res: res > 0
        ]

        super(Question92, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_residence_time(volume_km3, area_km2, precip_in_per_year):
        """
        Estimate the residence time of water in a reservoir assuming steady state.
        Parameters:
        - volume_km3: volume of the reservoir in km^3
        - area_km2: area over which precipitation falls in km^2
        - precip_in_per_year: precipitation in inches/year
        Returns:
        - Residence time in years
        """
        # Constants
        inch_to_meter = 0.0254
        km2_to_m2 = 1e6
        km3_to_m3 = 1e9

        # Convert all to SI units
        volume_m3 = volume_km3 * km3_to_m3
        area_m2 = area_km2 * km2_to_m2
        precip_m_per_year = precip_in_per_year * inch_to_meter

        # Calculate annual inflow
        inflow_m3_per_year = area_m2 * precip_m_per_year

        # Residence time (years)
        residence_time_years = volume_m3 / inflow_m3_per_year

        return Answer(residence_time_years, "yrs", 0)

if __name__ == '__main__':
    q = Question92(unique_id="q")
    print(q.question())
    print(q.answer())