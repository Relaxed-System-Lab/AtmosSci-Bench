import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question95(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """Estimating potential evapotranspiration through the measurement of water volume changes in an evaporation pan is a common method. United States Class A evaporation pans are cylindrical and have the following dimensions: depth = {depth_in} inches and diameter = {diameter_in} inches. An evaporation pan acts as a hydrological system with inflow, outflow, and storage volume components.

(a) Determine the cross-sectional area (m^2) of a United States Class A evaporation pan that allows water inflows and outflows. Also, compute the total storage volume of the pan (m^3).

(b) Initially, the pan holds {initial_gal} U.S. gallons of water. Find the depth of the water in the pan (mm).

(c) Given a water density of {density_kg_m3} kg/m^3, calculate the mass (kg) of water contained in the pan.

(d) After {evaporation_duration_hr} hours in an open area (without precipitation), the pan is inspected, revealing a remaining water volume of {final_gal_no_rain} gallons. Calculate the average evaporation rate (mm/hr) from the pan.

(e) The pan is emptied and refilled with {initial_gal} gallons of water, then left in an open area for another {evaporation_duration_hr} hours. During this time, rain occurred for {rain_duration_hr} hours at a steady rate of {rain_intensity_mm_hr} mm/hr; after {evaporation_duration_hr} hours, the water volume in the pan was {final_gal_with_rain} gallons. Determine the average evaporation rate (mm/hr) from the pan during this interval.

(f) Assuming the evaporation rate derived in E remains constant and no further precipitation takes place, estimate the duration (days) required for the pan to become empty due to evaporation."""

        self.func = self.calculate_evaporation_metrics

        self.default_variables = {
            "diameter_in": 47.5,
            "depth_in": 10.0,
            "initial_gal": 10.0,
            "final_gal_no_rain": 9.25,
            "final_gal_with_rain": 11.5,
            "rain_duration_hr": 3,
            "rain_intensity_mm_hr": 2.5,
            "density_kg_m3": 997.07,
            "evaporation_duration_hr": 24
        }

        self.constant = {
        }

        self.independent_variables = {
            "diameter_in": {"min": 30, "max": 60, "granularity": 0.5},
            "depth_in": {"min": 5, "max": 20, "granularity": 0.5},
            "initial_gal": {"min": 5, "max": 20, "granularity": 0.5},
            "rain_intensity_mm_hr": {"min": 0.5, "max": 10, "granularity": 0.1},
            "rain_duration_hr": {"min": 1, "max": 12, "granularity": 0.5},
            "evaporation_duration_hr": {"min": 1, "max": 48, "granularity": 1},
            "density_kg_m3": {"min": 990, "max": 1005, "granularity": 0.1}
        }

        self.dependent_variables = {
            "final_gal_no_rain": lambda vars: vars["initial_gal"] - 0.75,
            "final_gal_with_rain": lambda vars: vars["initial_gal"] + 1.5,
        }

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["final_gal_no_rain"] < vars["initial_gal"] and vars["final_gal_with_rain"] > vars["initial_gal"]
        ]

        super(Question95, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_evaporation_metrics(diameter_in, depth_in, initial_gal, final_gal_no_rain,
                                      final_gal_with_rain, rain_duration_hr, rain_intensity_mm_hr,
                                      density_kg_m3, evaporation_duration_hr):
        INCH_TO_M = 0.0254
        GAL_TO_M3 = 0.003785
        MM_TO_M = 0.001

        radius_m = (diameter_in * INCH_TO_M) / 2
        depth_m = depth_in * INCH_TO_M
        area_m2 = math.pi * radius_m ** 2
        total_volume_m3 = area_m2 * depth_m

        init_volume_m3 = initial_gal * GAL_TO_M3
        depth_mm = (init_volume_m3 / area_m2) * 1000

        mass_kg = init_volume_m3 * density_kg_m3

        delta_vol_no_rain = (initial_gal - final_gal_no_rain) * GAL_TO_M3
        evap_rate_mm_hr_d = (delta_vol_no_rain / evaporation_duration_hr / area_m2) * 1000

        delta_vol_with_rain = (final_gal_with_rain - initial_gal) * GAL_TO_M3
        avg_rain_mm_hr = (rain_duration_hr * rain_intensity_mm_hr) / evaporation_duration_hr
        evap_rate_mm_hr_e = avg_rain_mm_hr - ((delta_vol_with_rain / evaporation_duration_hr) / area_m2 * 1000)

        current_volume_m3 = final_gal_with_rain * GAL_TO_M3
        evap_rate_m_hr_e = evap_rate_mm_hr_e * MM_TO_M
        time_hr_to_empty = current_volume_m3 / (evap_rate_m_hr_e * area_m2)
        time_days_to_empty = time_hr_to_empty / 24

        return NestedAnswer({
            "(a)": NestedAnswer({
                "cross_sectional_area_m2": Answer(area_m2, "m^2", 2),
                "total_storage_volume_m3": Answer(total_volume_m3, "m^3", 2)
            }),
            "(b)": Answer(depth_mm, "mm", 2),
            "(c)": Answer(mass_kg, "kg", 2),
            "(d)": Answer(evap_rate_mm_hr_d, "mm/hr", 2),
            "(e)": Answer(evap_rate_mm_hr_e, "mm/hr", 2),
            "(f)": Answer(time_days_to_empty, "days", 2)
        })


if __name__ == '__main__':
    q = Question95(unique_id="q")
    print(q.question())
    print(q.answer())