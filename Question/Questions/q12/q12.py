import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question12(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """
Show that a homogeneous atmosphere (density independent of height) has a finite height that depends only on the temperature at the lower boundary. 
Compute the height of a homogeneous atmosphere with surface temperature T0={T0} K and surface pressure p0={p0} hPa. 
(Use the ideal gas law and hydrostatic balance.)
        """
        self.func = self.calculate_height
        self.default_variables = {
            "T0": 273,  # Surface temperature in Kelvin
            "p0": 1000,  # Surface pressure in hPa
        }

        self.constant = {
            "g": 9.8,    # Gravitational acceleration in m/s²
            "R": 287     # Gas constant for air in J/(kg·K)
        }

        self.independent_variables = {
            "T0": {"min": 100, "max": 400, "granularity": 1},
            "p0": {"min": 500, "max": 1200, "granularity": 10},
        }

        self.dependent_variables = {}
        self.choice_variables = {}
        self.custom_constraints = [
            lambda vars, res: res > 0  # The height must always be positive
        ]
        super(Question12, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_height(T0, p0, g, R):
        """
        Calculate the finite height of a homogeneous atmosphere.

        Parameters:
            T0 (float): Surface temperature in Kelvin (K).
            p0 (float): Surface pressure in hPa (converted to Pa).
            g (float): Gravitational acceleration in m/s².
            R (float): Ideal gas constant for air in J/(kg·K).

        Returns:
            float: The height of the homogeneous atmosphere in kilometers (km).
        """
        # Convert surface pressure from hPa to Pa
        p0_pa = p0 * 100  # 1 hPa = 100 Pa
        
        # Calculate the height of the homogeneous atmosphere
        H = (R * T0) / g  # Height in meters
        H_km = H / 1000   # Convert meters to kilometers
        
        return Answer(H_km, "km", 2)

if __name__ == '__main__':
    q = Question12(unique_id="q")
    print(q.question())
    print(q.answer())