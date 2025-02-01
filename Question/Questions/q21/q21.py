import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer

class Question21(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """ Find the average vorticity within a cylindrical annulus of inner radius {inner_radius_km} km and outer radius {outer_radius_km} km if the tangential velocity distribution is given by $V=A / r$, where $A={A} \mathrm{{~m}}^{{2}} \mathrm{{~s}}^{{-1}}$ and $r$ is in meters. What is the average vorticity within the inner circle of radius {inner_radius_km} km? """
        self.func = self.compute_vorticity
        self.default_variables = {
            "inner_radius_km": 200,
            "outer_radius_km": 400,
            "A": 1e6
        }

        self.constant = {}

        self.independent_variables = {
            "inner_radius_km": {"min": 100, "max": 300, "granularity": 10},
            "outer_radius_km": {"min": 300, "max": 500, "granularity": 10},
            "A": {"min": 1e5, "max": 1e7, "granularity": 1e5}
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["inner_radius_km"] < vars["outer_radius_km"]
        ]

        super(Question21, self).__init__(unique_id, seed, variables)


    @staticmethod
    def compute_vorticity(inner_radius_km, outer_radius_km, A):
        """
        Compute the average vorticity within a cylindrical annulus and within an inner circle.

        Parameters:
            inner_radius_km (float): Inner radius in kilometers.
            outer_radius_km (float): Outer radius in kilometers.
            A (float): Tangential velocity distribution constant in m^2/s.

        Returns:
            tuple: (vorticity_annulus, vorticity_inner_circle) in s^-1.
        """
        import math

        # Convert radii to meters
        inner_radius_m = inner_radius_km * 1000
        outer_radius_m = outer_radius_km * 1000

        # Circulation for outer circle
        circulation_outer = 2 * math.pi * outer_radius_m * (A / outer_radius_m)

        # Circulation for inner circle (clockwise, thus negative)
        circulation_inner = -2 * math.pi * inner_radius_m * (A / inner_radius_m)

        # Total circulation in the annular region
        total_circulation_annulus = circulation_outer + circulation_inner

        # Area of annulus
        area_annulus = math.pi * (outer_radius_m**2 - inner_radius_m**2)

        # Average vorticity in the annulus
        if area_annulus != 0:
            vorticity_annulus = total_circulation_annulus / area_annulus
        else:
            vorticity_annulus = 0

        # Circulation within the inner circle
        circulation_inner_circle = 2 * math.pi * A

        # Area of the inner circle
        area_inner_circle = math.pi * (inner_radius_m**2)

        # Average vorticity within the inner circle
        if area_inner_circle != 0:
            vorticity_inner_circle = circulation_inner_circle / area_inner_circle
        else:
            vorticity_inner_circle = 0

        return NestedAnswer({
            "vorticity_annulus": Answer(vorticity_annulus, "s^-1", 6),
            "vorticity_inner_circle": Answer(vorticity_inner_circle, "s^-1", 6)
        })

if __name__ == '__main__':
    q = Question21(unique_id="q")
    print(q.question())
    print(q.answer())