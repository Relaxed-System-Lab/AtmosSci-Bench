import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question96(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """A small catchment with an {area_ha} ha area in Iowa absorbs an average R_n = {R_n} W m^-2 in June. Use the energy balance method to estimate the catchment's evapotranspiration for June.

(a) Formulate a comprehensive energy balance equation, including all terms, for the catchment in June.

(b) By ignoring ground conduction (G) and assuming no change in stored energy (dQ/dt = 0), simplify the energy balance equation for the catchment to solve for the latent heat flux, E_l. Substitute H (the sensible heat flux) with B × E_l, where B is the Bowen ratio.

(c) Given a mean Bowen ratio of {B} for the catchment, determine the mean daily latent heat flux to the atmosphere (W m^-2) and the mean evapotranspiration rate (mm day^-1) from the catchment. Assume a water density, ρ_w = {rho_w} kg m^-3.

(d) Compute the total evapotranspiration from the catchment over the month of June ({days} days)."""

        self.func = self.calculate_evapotranspiration

        self.default_variables = {
            "area_ha": 300,
            "R_n": 330,
            "B": 0.2,
            "rho_w": 1000.0,
            "lambda_v": 2.45e6,
            "days": 30
        }

        self.constant = {
            # No fixed constants beyond defaults already covered
        }

        self.independent_variables = {
            "R_n": {"min": 100, "max": 500, "granularity": 1},
            "B": {"min": 0.1, "max": 1.0, "granularity": 0.01},
            "rho_w": {"min": 900, "max": 1100, "granularity": 10},
            "lambda_v": {"min": 2.3e6, "max": 2.6e6, "granularity": 1e4},
            "days": {"min": 28, "max": 31, "granularity": 1}
        }

        self.dependent_variables = {
            "area_ha": lambda vars: 300  # Constant in this context
        }

        self.choice_variables = {
            # No discrete choice groups in this case
        }

        self.custom_constraints = [
            lambda vars, res: res["(c)"] > 0 and res["(d)"] > 0  # Ensure evapotranspiration is physically meaningful
        ]

        super(Question96, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_evapotranspiration(R_n, B, rho_w, lambda_v, days, area_ha):
        """
        Calculate:
        A. Energy balance equation (text output)
        B. Simplified formula for latent heat flux
        C. Daily evapotranspiration rate (mm/day)
        D. Total evapotranspiration over given days (mm)
        """
        # A. Full energy balance equation (string)
        energy_balance_eq = "dQ/dt = R_n - G - H - E_l"

        # B. Simplified symbolic expression
        latent_heat_flux_expr = "E_l = R_n / (1 + B)"

        # C. Numerical computation
        E_l = R_n / (1 + B)  # latent heat flux in W/m^2
        et_m_per_s = E_l / (rho_w * lambda_v)
        et_mm_per_day = et_m_per_s * 1000 * 86400
        total_et_mm = et_mm_per_day * days

        return NestedAnswer({
            "(a)": Answer(energy_balance_eq, "", None),
            "(b)": Answer(latent_heat_flux_expr, "", None),
            "(c)": Answer(et_mm_per_day, "mm/day", 2),
            "(d)": Answer(total_et_mm, "mm", 2)
        })
if __name__ == '__main__':
    q = Question96(unique_id="q")
    print(q.question())
    print(q.answer())