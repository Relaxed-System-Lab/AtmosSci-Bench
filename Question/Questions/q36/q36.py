import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question36(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Physical Oceanography"
        self.template = """
Consider an ocean of uniform density {rho_ref} kg/m^3.
(a) From the hydrostatic relationship, determine the pressure at a depth of {depth1} m and at {depth2} m. Express your answer in units of atmospheric surface pressure, {{p_s}} mbar = {p_s_pascal} Pa.

(b) Given that the heat content of an elementary mass dm of dry air at temperature T is $c_{{p}} * T * dm (where $c_{{p}} is the specific heat of air at constant pressure), find a relationship for, and evaluate, the (vertically integrated) heat capacity (heat content per degree Kelvin) of the atmosphere per unit horizontal area. Find how deep an ocean would have to be in order to have the same heat capacity per unit horizontal area.

        """
        self.func = self.calculate_ocean_properties
        self.default_variables = {
            "depth1": 1000,             # Depth 1 (m)
            "depth2": 5000,             # Depth 2 (m)
        }

        self.constant = {
            "rho_ref": 1000,            # Ocean density (kg/m^3)
            "cp_air": 1004,             # Specific heat of air at constant pressure (J/(kg·K))
            "cp_water": 4187,           # Specific heat of water (J/(kg·K))
            "rho_water": 1000,          # Water density (kg/m^3)
            "g": 9.81,                  # Gravitational acceleration (m/s^2)
            "p_s": 1000,                # Atmospheric surface pressure (mbar)
            "p_s_pascal": 1e5,          # Atmospheric surface pressure (Pa)
        }

        self.independent_variables = {
            "depth1": {"min": 500, "max": 2000, "granularity": 1},
            "depth2": {"min": 4000, "max": 6000, "granularity": 1},
        }

        self.dependent_variables = {
            # "surface_pressure": lambda vars: self.constant["p_s_pascal"]
        }

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["depth1"] < vars["depth2"]
        ]

        super(Question36, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_ocean_properties(
        rho_ref, g, depth1, depth2, p_s, p_s_pascal, cp_air, cp_water, rho_water
    ):
        """
        Calculate the pressure at specified depths and the equivalent ocean depth for heat capacity.
        """
        surface_pressure = p_s_pascal

        # (a) Hydrostatic pressure at depths
        pressure_at_depth1 = p_s_pascal * (1 + (g * rho_ref * depth1) / p_s_pascal)
        pressure_at_depth2 = p_s_pascal * (1 + (g * rho_ref * depth2) / p_s_pascal)
        pressure_at_depth1_atm = pressure_at_depth1 / p_s_pascal
        pressure_at_depth2_atm = pressure_at_depth2 / p_s_pascal

        # (b) Vertically integrated heat capacity of atmosphere
        heat_capacity_atmosphere = (cp_air * surface_pressure) / g

        # Equivalent ocean depth for same heat capacity
        equivalent_ocean_depth = heat_capacity_atmosphere / (cp_water * rho_water)

        return NestedAnswer({
            "(a)": NestedAnswer({
                f"pressure_at_{depth1}m": Answer(pressure_at_depth1_atm, "p_s", 1),
                f"pressure_at_{depth2}m": Answer(pressure_at_depth2_atm, "p_s", 1)
            }),
            "(b)": NestedAnswer({
                "heat_capacity_atmosphere": Answer(heat_capacity_atmosphere, "JK/(m^2)", -5),
                "equivalent_ocean_depth": Answer(equivalent_ocean_depth, "m", 2)
            })
        })


if __name__ == '__main__':
    q = Question36(unique_id="q")
    print(q.question())
    print(q.answer())