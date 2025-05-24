import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question102(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"

        self.template = """In regions where irrigation is applied to boost agricultural output, maintaining soil water content above the permanent wilting point (e.g., θ ≥ 2 θw) during the growing season is essential. The root zone soil moisture should not surpass field capacity θfc during irrigation, as exceeding θfc results in drainage losses of water and fertilizer. Under this strategy, soil moisture stays below field capacity, with evapotranspiration being the sole loss from the root zone. Assuming the absence of rainfall, the temporal changes in average soil moisture θ in the root zone are described by the soil water balance equation:

Z * dθ/dt = -et,

where Z represents the depth of the root zone. This implies that variations in stored water within the control volume (i.e., the root zone) arise from the disparity between water inputs and outputs. In this scenario, there are no inputs from rainfall, and the only outflow is due to et. The irrigation period (i.e., the interval between successive irrigation applications) is determined by integrating the soil water balance equation from time t=0, when θ=θfc (immediately after irrigation), to time ti, when θ=θ0 (indicating it's time to irrigate again). This assumes the evapotranspiration rate decreases linearly from the potential rate PET at θ = θfc to zero at θ = θw (i.e., et = PET*(θ - θw)/(θfc - θw)):

Determine the irrigation period ti given:
Z={Z} m, PET={PET} mm/day, θfc={theta_fc}, θw={theta_w}, and θ0={theta_0}."""

        self.func = self.calculate_irrigation_period

        self.default_variables = {
            "theta_fc": 0.19,  # Field capacity (m³/m³)
            "theta_w": 0.05,   # Wilting point (m³/m³)
            "Z": 0.40,         # Root zone depth (m)
            "PET": 6.0,        # Potential evapotranspiration rate (mm/day)
            "theta_0": 0.10    # Moisture threshold for irrigation (e.g., 2*theta_w)
        }

        self.constant = {}

        self.independent_variables = {
            "theta_fc": {"min": 0.15, "max": 0.40, "granularity": 0.01},
            "theta_w": {"min": 0.01, "max": 0.15, "granularity": 0.01},
            "Z": {"min": 0.10, "max": 2.00, "granularity": 0.01},
            "PET": {"min": 1.0, "max": 10.0, "granularity": 0.1},
        }

        self.dependent_variables = {
            "theta_0": lambda vars: round(2 * vars["theta_w"], 4),
        }

        self.choice_variables = {
        }

        self.custom_constraints = [
            lambda vars, res: vars["theta_w"] < vars["theta_fc"],
            lambda vars, res: vars["theta_w"] < vars["theta_0"] < vars["theta_fc"]
        ]

        super(Question102, self).__init__(unique_id, seed, variables)



    @staticmethod
    def calculate_irrigation_period(theta_fc, theta_w, Z, PET, theta_0):
        """
        Calculate the irrigation period (ti) using the water balance equation:
        ti = [Z * (theta_fc - theta_w) / PET] * ln[(theta_fc - theta_w) / (theta_0 - theta_w)]

        Parameters:
        - theta_fc (float): Field capacity
        - theta_w (float): Wilting point
        - Z (float): Root zone depth (m)
        - PET (float): Potential evapotranspiration (mm/day)
        - theta_0 (float): Threshold soil moisture content triggering irrigation

        Returns:
        - ti (float): Irrigation period (days)
        """
        PET_m = PET / 1000  # Convert PET from mm/day to m/day
        numerator = Z * (theta_fc - theta_w)
        log_term = math.log((theta_fc - theta_w) / (theta_0 - theta_w))
        ti = numerator / PET_m * log_term
        return Answer(ti, "days", 2)


if __name__ == '__main__':
    q = Question102(unique_id="q")
    print(q.question())
    print(q.answer())