import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question66(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """ 
The azimuthal velocity component in some hurricanes is observed to have a radial dependence given by 
$v_{{\\lambda}}=V_{{0}}\\left(r_{{0}} / r\\right)^{{2}}$ for distances from the center given by $r \\geq r_{{0}}$. 
Letting $V_{{0}}={V0} \\mathrm{{~m}} \\mathrm{{~s}}^{{-1}}$ and $r_{{0}}={r0} \\mathrm{{~km}}$, find the total geopotential difference 
between the far field $(r \\rightarrow \\infty)$ and $r=r_{{0}}$, assuming gradient wind balance and 
$f_{{0}}={f0} \\mathrm{{~s}}^{{-1}}$. At what distance from the center does the Coriolis force equal the centrifugal force?
        """
        self.func = self.hurricane_geopotential_difference
        self.default_variables = {
            "V0": 50.0,  # Maximum azimuthal velocity (m/s)
            "r0": 50.0,  # Radius of maximum wind (km)

        }

        self.constant = {
            "f0": 5e-5,  # Coriolis parameter (s^-1)
        }

        self.independent_variables = {
            "V0": {"min": 10.0, "max": 100.0, "granularity": 0.1},
            "r0": {"min": 10.0, "max": 200.0, "granularity": 0.1},
        #    "f0": {"min": 1e-5, "max": 1e-4, "granularity": 1e-6},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = []
        super(Question66, self).__init__(unique_id, seed, variables)


    @staticmethod
    def hurricane_geopotential_difference(V0, r0, f0):
        """
        Calculate the total geopotential difference and the distance where Coriolis force equals the centrifugal force.

        Parameters:
            V0 (float): Maximum azimuthal velocity in m/s.
            r0 (float): Radius of maximum wind in km.
            f0 (float): Coriolis parameter in s^-1.

        Returns:
            tuple: (geopotential_difference, balance_distance_km)
                    geopotential_difference (float): Total geopotential difference in m^2/s^2.
                    balance_distance_km (float): Distance where Coriolis equals centrifugal force in km.
        """
        # Convert r0 from km to meters
        r0_m = r0 * 1e3

        # Geopotential difference calculation
        term1 = V0**2 / 4
        term2 = f0 * V0 * r0_m
        geopotential_difference = term1 + term2

        # Distance where Coriolis force equals centrifugal force
        r_balance_cubed = (V0 * r0_m**2) / f0
        balance_distance = r_balance_cubed**(1/3)

        # Convert balance distance back to km
        balance_distance_km = balance_distance / 1e3

        return NestedAnswer({
            "geopotential_difference": Answer(geopotential_difference, "m^2/s^2", 0),
            "balance_distance_km": Answer(balance_distance_km, "km", 1)
        })



if __name__ == '__main__':
    q = Question66(unique_id="q")
    print(q.question())
    print(q.answer())