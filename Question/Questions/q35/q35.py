import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question35(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """Consider the tropical Hadley circulation in northern winter. The circulation rises at {phi_initial}°S, moves northward across the equator in the upper troposphere, and sinks at {phi_final}°N. Assuming that the circulation, outside the near-surface boundary layer, is zonally symmetric (independent of x) and inviscid (and thus conserves absolute angular momentum about the Earth's rotation axis), and that it leaves the boundary layer at {phi_initial}°S with zonal velocity u={u_initial} m/s, calculate the zonal wind in the upper troposphere at (a) the equator, (b) at {phi_middle}°N, and (c) at {phi_final}°N.
"""
        self.func = self.calculate_zonal_wind
        self.default_variables = {
            "phi_initial": 10,     # Latitude where circulation starts (degrees, south is negative)
            "phi_final": 20,        # Latitude where circulation sinks (degrees, north is positive)
            "phi_middle": 10,      # Latitude for first calculation (degrees, north is positive)
        #   "phi_middle2": 20,      # Latitude for second calculation (degrees, north is positive)
            "u_initial": 0         # Initial zonal wind velocity (m/s)
        }
        self.constant = {
            "Omega_a2": 2.952e9,  # Given as constant in the problem
            "angular_velocity": 2 * 3.141592653589793 / 86400,  # Earth's angular velocity (rad/s)
            "earth_radius": 6.371e6 # Radius of Earth (m)
        }
        self.independent_variables = {
            "phi_initial": {"min": 15, "max": 25, "granularity": 1},  # South latitudes
            "phi_final": {"min": 15, "max": 25, "granularity": 1},    # North latitudes
            "phi_middle": {"min": 5, "max": 15, "granularity": 1},   # Intermediate latitude (10°N)
        #   "phi_middle2": {"min": 15, "max": 25, "granularity": 1},  # North latitude (20°N)
        }
        self.dependent_variables = {
            "u_initial": lambda vars: 0,  # u_initial is typically 0 in such problems
        }
        self.choice_variables = {}
        self.custom_constraints = [
        #   lambda vars, res: vars["phi_initial"] < 0,  # phi_initial should be in the southern hemisphere
        #   lambda vars, res: vars["phi_final"] > 0,    # phi_final should be in the northern hemisphere
        #   lambda vars, res: vars["phi_middle1"] > 0,  # Intermediate latitude must be north
            lambda vars, res: vars["phi_final"] > vars["phi_middle"]
        ]

        super(Question35, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_zonal_wind(phi_initial, phi_final, phi_middle, u_initial, angular_velocity, earth_radius, Omega_a2):
        """
        Calculate the zonal wind in the upper troposphere at specified latitudes.
        """
        import math

        # M0 calculation at phi_initial
        phi_initial_rad = math.radians(phi_initial)
        M0 = Omega_a2 * math.cos(phi_initial_rad)**2

        def zonal_wind(phi):
            phi_rad = math.radians(phi)
            M_phi = Omega_a2 * math.cos(phi_rad)**2
            return (M0 - M_phi) / (earth_radius * math.cos(phi_rad))

        results = NestedAnswer({
            "(a)": Answer(zonal_wind(0), "m/s", 1),              # At the equator
            "(b)": Answer(zonal_wind(phi_middle), "m/s", 1),  # At 10°N
            "(c)": Answer(zonal_wind(phi_final), "m/s", 1)   # At 20°N
        })
        return results


if __name__ == '__main__':
    q = Question35(unique_id="q")
    print(q.question())
    print(q.answer())