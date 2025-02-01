import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np

class Question79(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """
Using (i) equation which relates the saturation vapor pressure of $ \\mathrm{{H}}_{{2}} \\mathrm{{O}} $ to temperature $ T $, and (ii) the equation of state of water vapor $ e = \\rho_{{v}} R_{{v}} T $, compute the maximum amount of water vapor per unit volume that air can hold at the surface, where $ T_{{s}}={T_surface} \\mathrm{{~K}} $, and at a height of 10 km where $ T_{{10}} \\mathrm{{~km}}={T_altitude} \\mathrm{{~K}} $. Express your answer in $\\mathrm{{kg}} \\mathrm{{m}}^{{-3}} $.
        """
        self.func = self.calculate_water_vapor_density
        self.default_variables = {
            "T_surface": 288,  # Temperature at the surface (K)
            "T_altitude": 220,  # Temperature at 10 km altitude (K)
        }

        self.constant = {
            "Rv": 461,  # Specific gas constant for water vapor (J/kg/K)
            "es_base": 6.11e2,  # Base saturation vapor pressure (Pa)
            "coef": 0.067  # Exponential coefficient for temperature dependence
        }

        self.independent_variables = {
            "T_surface": {"min": 250, "max": 310, "granularity": 1},
            "T_altitude": {"min": 200, "max": 250, "granularity": 1},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["T_surface"] > vars["T_altitude"]
        ]

        super(Question79, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_water_vapor_density(T_surface, T_altitude, Rv, es_base, coef):
        """
        Calculate the maximum water vapor density at saturation at the surface and at a given altitude.

        Parameters:
            T_surface (float): Temperature at the surface (K).
            T_altitude (float): Temperature at the altitude (K).
            Rv (float): Specific gas constant for water vapor (J/kg/K).
            es_base (float): Base saturation vapor pressure (Pa).
            coef (float): Exponential coefficient for temperature dependence.

        Returns:
            tuple: Maximum water vapor densities at the surface and altitude (kg/m^3).
        """
        # Saturation vapor pressure at the surface
        es_surface = es_base * math.exp(coef * (T_surface - 273))
        rho_v_surface = es_surface / (Rv * T_surface)

        # Saturation vapor pressure at the altitude
        es_altitude = es_base * math.exp(coef * (T_altitude - 273))
        rho_v_altitude = es_altitude / (Rv * T_altitude)

        # return NestedAnswer([Answer(rho_v_surface, "kg/m^3", 5), Answer(rho_v_altitude, "kg/m^3", 6)])
        return NestedAnswer({
            "Surface": Answer(rho_v_surface, "kg/m^3", 5),
            "Altitude": Answer(rho_v_altitude, "kg/m^3", 6)
        })


if __name__ == '__main__':
    q = Question79(unique_id="q")
    print(q.question())
    print(q.answer())