import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question93(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """In a typical year, a small agricultural catchment with an {area} km² area receives {precip_mm} mm of rainfall. The catchment is drained by a stream with continuous discharge records. The total annual surface-water runoff, as derived from the stream discharge data, amounts to {runoff_volume_m3} m³.
(a) Compute the annual volume of water lost to evapotranspiration in cubic meters, assuming there is no change in water storage in the catchment.
(b) Find the depth of water lost to evapotranspiration over the year in millimeters, assuming once more no change in water storage within the catchment.
(c) Calculate the runoff ratio (runoff over precipitation) for the catchment."""

        self.func = self.calculate_evapotranspiration_metrics

        self.default_variables = {
            "area": 3.0,                 # km²
            "precip_mm": 950.0,         # mm
            "runoff_volume_m3": 1.1e6   # m³
        }

        self.constant = {
        }

        self.independent_variables = {
            "area": {"min": 0.1, "max": 100.0, "granularity": 0.1},
            "precip_mm": {"min": 100.0, "max": 3000.0, "granularity": 10.0},
        }

        self.dependent_variables = {
            "runoff_volume_m3": lambda vars: 0.2 * vars["area"] * vars["precip_mm"] * 1_000  # crude approx for dependency
        }

        self.choice_variables = {
            "catchment_example": [
                {"area": 3.0, "precip_mm": 950.0, "runoff_volume_m3": 1.1e6},
                {"area": 10.0, "precip_mm": 1200.0, "runoff_volume_m3": 2.5e6},
                {"area": 5.0, "precip_mm": 800.0, "runoff_volume_m3": 0.9e6},
            ]
        }

        self.custom_constraints = [
            lambda vars, res: vars["runoff_volume_m3"] < vars["precip_mm"] * vars["area"] * 1000
        ]
        super(Question93, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_evapotranspiration_metrics(area, precip_mm, runoff_volume_m3):
        """
        Calculate evapotranspiration volume (m³), depth (mm), and runoff ratio for a catchment.

        Parameters:
        - area: Catchment area in km²
        - precip_mm: Annual precipitation in mm
        - runoff_volume_m3: Annual surface runoff volume in m³

        Returns:
        - evapotranspiration_volume_m3: Total volume of evapotranspiration (m³)
        - evapotranspiration_depth_mm: Depth of evapotranspiration (mm)
        - runoff_ratio: runoff / precipitation
        """
        area_m2 = area * 1_000_000                     # Convert km² to m²
        precip_m = precip_mm / 1000.0                  # Convert mm to m
        total_precip_volume_m3 = precip_m * area_m2    # Total volume of precipitation
        evapotranspiration_volume_m3 = total_precip_volume_m3 - runoff_volume_m3
        evapotranspiration_depth_mm = (evapotranspiration_volume_m3 / area_m2) * 1000.0
        runoff_ratio = runoff_volume_m3 / total_precip_volume_m3

        return NestedAnswer({
            "(a)": Answer(evapotranspiration_volume_m3, "m^3", 2),
            "(b)": Answer(evapotranspiration_depth_mm, "mm", 2),
            "(c)": Answer(runoff_ratio, "", 4)
        })


if __name__ == '__main__':
    q = Question93(unique_id="q")
    print(q.question())
    print(q.answer())