import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question86(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Physical Oceanography"
        self.template = """Warm western boundary currents like the {name} are crucial to the climate system due to their role in meridional heat transport. The {name} measures approximately {width_km} km in width, extends to a depth of {depth_m} m, and has an average speed of {speed_m_s} m/s.

a. Estimate the volume transport of the {name} (in Sv).

b. Estimate the temperature difference (ΔT = {delta_T_C} °C) and the meridional heat transport linked with the {name}."""
        self.func = self.calculate_transport

        self.default_variables = {
            "speed_m_s": 1.0,
            "depth_m": 500,
            "width_km": 100,
            "delta_T_C": 5.0,
            "name": "Gulf Stream"
        }

        self.constant = {
            # "density_kg_m3": 1025,              # Seawater density
            # "specific_heat_J_kg_C": 3993        # Specific heat of seawater
        }

        self.independent_variables = {
            "speed_m_s": {"min": 0.1, "max": 2.0, "granularity": 0.1},
            "depth_m": {"min": 100, "max": 1000, "granularity": 10},
            "width_km": {"min": 10, "max": 200, "granularity": 10},
            "delta_T_C": {"min": 1, "max": 10, "granularity": 0.5}
        }

        self.dependent_variables = {
            # No strict dependencies here — all can be randomly generated
        }

        self.choice_variables = {
            "current": [
                {"name": "Gulf Stream"},
                {"name": "Kuroshio"},
                {"name": "Agulhas"},
                {"name": "Brazil Current"},
                {"name": "East Australian Current"},
                {"name": "Loop Current"},
                {"name": "Mindanao Current"},
                {"name": "Mozambique Current"},
                {"name": "North Brazil Current"},
                {"name": "Caribbean Current"},
                {"name": "Antilles Current"},
                {"name": "Canary Current"},
                {"name": "Benguela Current"},
                {"name": "Alaska Current"},
                {"name": "Norwegian Current"},
                {"name": "California Current"},
                {"name": "Irminger Current"},
                {"name": "East Greenland Current"},
                {"name": "Somali Current"},
                {"name": "South Equatorial Current"}
            ]
        }

        self.custom_constraints = [
            lambda vars, res: vars["depth_m"] > 0 and vars["width_km"] > 0
        ]

        super(Question86, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_transport(speed_m_s, depth_m, width_km, delta_T_C, name):
        """
        Calculates volume transport (Sv) and meridional heat transport (PW)
        of a warm western boundary current like the Gulf Stream.

        Parameters:
        - speed_m_s: Flow velocity (m/s)
        - depth_m: Depth of the current (m)
        - width_km: Width of the current (km)
        - delta_T_C: Temperature difference (°C)

        Returns:
        - Tuple: (volume_transport_Sv, heat_transport_PW)
        """

        # Constants
        density = 1025  # kg/m³
        specific_heat = 3993  # J/kg·°C

        # Convert width to meters
        width_m = width_km * 1e3

        # Volume transport (m³/s)
        volume_transport_m3_s = speed_m_s * depth_m * width_m
        volume_transport_Sv = volume_transport_m3_s / 1e6

        # Heat transport (W)
        heat_transport_W = density * specific_heat * speed_m_s * delta_T_C * depth_m * width_m
        heat_transport_PW = heat_transport_W / 1e15

        return NestedAnswer({
            "volume_transport_Sv": Answer(volume_transport_Sv, "Sv", 4),
            "heat_transport_PW": Answer(heat_transport_PW, "PW", 4)
        })

if __name__ == '__main__':
    q = Question86(unique_id="q")
    print(q.question())
    print(q.answer())