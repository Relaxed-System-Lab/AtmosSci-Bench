import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question97(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """A thermometer floating with the river's flow at {drift_speed_km_hr} km/hr measures the surface temperature. The overall warming rate of the river water is {dT_dt_partial_C_hr} °C/hr, while the temperature rises by {dT_dx_C_km} °C per kilometer downstream. What is the temperature change (°C) recorded by the thermometer over {duration_hr} hours?"""

        self.func = self.compute_temperature_change

        self.default_variables = {
            "drift_speed_km_hr": 1.0,
            "dT_dt_partial_C_hr": 0.2,
            "dT_dx_C_km": 0.1,
            "duration_hr": 6
        }

        self.constant = {}

        self.independent_variables = {
            "drift_speed_km_hr": {"min": 0.5, "max": 5.0, "granularity": 0.1},
            "dT_dt_partial_C_hr": {"min": 0.0, "max": 1.0, "granularity": 0.01},
            "dT_dx_C_km": {"min": 0.0, "max": 0.5, "granularity": 0.01},
            "duration_hr": {"min": 1, "max": 24, "granularity": 1}
        }

        self.dependent_variables = {}

        self.choice_variables = {
            "river_condition": [
                {"drift_speed_km_hr": 0.5, "dT_dt_partial_C_hr": 0.1, "dT_dx_C_km": 0.05, "duration_hr": 4},
                {"drift_speed_km_hr": 2.0, "dT_dt_partial_C_hr": 0.3, "dT_dx_C_km": 0.2, "duration_hr": 8}
            ]
        }

        self.custom_constraints = [
            lambda vars, res: res >= 0  # Temperature change must be non-negative
        ]


        super(Question97, self).__init__(unique_id, seed, variables)


    @staticmethod
    def compute_temperature_change(drift_speed_km_hr, dT_dt_partial_C_hr, dT_dx_C_km, duration_hr):
        """
        Computes the total temperature change recorded by a drifting thermometer in a river.

        Parameters:
        - drift_speed_km_hr: Speed of the thermometer drifting with the river (km/hr)
        - dT_dt_partial_C_hr: Local warming rate (°C/hr)
        - dT_dx_C_km: Temperature gradient along the stream (°C/km)
        - duration_hr: Time the thermometer is drifting (in hours)

        Returns:
        - float: Total temperature change recorded by the thermometer (°C)
        """
        # Total rate of temperature change from material derivative
        dT_dt_total_C_hr = dT_dt_partial_C_hr + drift_speed_km_hr * dT_dx_C_km

        # Compute total temperature change over duration
        temperature_change = dT_dt_total_C_hr * duration_hr

        return Answer(temperature_change, "°C", 2)


if __name__ == '__main__':
    q = Question97(unique_id="q")
    print(q.question())
    print(q.answer())