import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question91(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """Annually, a precipitation depth of {depth} meter is recorded over a catchment area measuring {area} (or $10^{{3}}$) $\mathrm{{km}}^{{2}}$.
(a) Calculate the total volume of water received in an average year in cubic meters.
(b) Convert this volume into gallons."""
        self.func = self.calculate_precipitation_volume

        self.default_variables = {
            "depth": 1.0,       # Precipitation depth in meters
            "area": 1000        # Catchment area in square kilometers
        }

        self.constant = {
            # "m3_to_gal": 264.2  # Conversion factor from m³ to gallons
        }

        self.independent_variables = {
            "depth": {"min": 0.01, "max": 5.0, "granularity": 0.01},
            "area": {"min": 1, "max": 10000, "granularity": 1}
        }

        self.dependent_variables = {
            # None for this question
        }

        self.choice_variables = {
            # No grouped categorical variables in this case
        }

        self.custom_constraints = [
            lambda vars, res: vars["depth"] > 0,
            lambda vars, res: vars["area"] > 0
        ]

        super(Question91, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_precipitation_volume(depth, area):
        """
        Calculate the volume of water received over a catchment.

        Parameters:
        - depth (float): Depth of precipitation in meters.
        - area (float): Area of the catchment in square kilometers.

        Returns:
        - (volume_m3, volume_gal): Tuple containing volume in cubic meters and gallons.
        """
        # Convert area from km² to m²
        area_m2 = area * 1e6

        # Volume in cubic meters
        volume_m3 = depth * area_m2

        # Conversion factor from m³ to gallons
        m3_to_gal = 264.2

        # Volume in gallons
        volume_gal = volume_m3 * m3_to_gal

        return NestedAnswer({
            "(a)": Answer(volume_m3, "m^3", 0),
            "(b)": Answer(volume_gal, "gal", 0)
        })

        super(Question91, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_precipitation_volume(depth, area):
        """
        Calculate the volume of water received over a catchment.

        Parameters:
        - depth (float): Depth of precipitation in meters.
        - area (float): Area of the catchment in square kilometers.

        Returns:
        - (volume_m3, volume_gal): Tuple containing volume in cubic meters and gallons.
        """
        # Convert area from km² to m²
        area_m2 = area * 1e6

        # Volume in cubic meters
        volume_m3 = depth * area_m2

        # Conversion factor from m³ to gallons
        m3_to_gal = 264.2

        # Volume in gallons
        volume_gal = volume_m3 * m3_to_gal

        return NestedAnswer({
            "(a)": Answer(volume_m3, "m^3", 0),
            "(b)": Answer(volume_gal, "gal", 0)
        })


if __name__ == '__main__':
    q = Question91(unique_id="q")
    print(q.question())
    print(q.answer())