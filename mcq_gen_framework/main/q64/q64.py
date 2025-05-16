import random, math
from question import Question
from answer import Answer, NestedAnswer


class Question64(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Geophysics"
        self.template = """Within a cylindrical annulus with permeable walls, having an inner radius of {inner_radius} cm, an outer radius of {outer_radius} cm, and a {depth} cm depth, the horizontal motion is constant with respect to height and azimuth. This motion is described by the formulas u=7-0.2r and v=40+2r, where u and v denote the radial and tangential velocity components in cm/s, oriented outward and counterclockwise, respectively, with r being the radial distance from the annulus center in cm. Given that the fluid is incompressible, determine 
(a) the circulation around the annular ring, 
(b) the mean vorticity within the annular ring, 
(c) the mean divergence inside the annular ring, and 
(d) the mean vertical velocity at the top of the annulus, assuming it is zero at the bottom."""
        self.func = self.calculate_cylindrical_annulus

        self.default_variables = {
            "inner_radius": 10.0,  # cm
            "outer_radius": 20.0,  # cm
            "depth": 10.0          # cm
        }

        self.constant = {
        }

        self.independent_variables = {
            "inner_radius": {"min": 5.0, "max": 15.0, "granularity": 0.1},
            "outer_radius": {"min": 16.0, "max": 25.0, "granularity": 0.1},
            "depth": {"min": 5.0, "max": 20.0, "granularity": 0.1},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["inner_radius"] < vars["outer_radius"]
        ]
        super(Question64, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_cylindrical_annulus(inner_radius, outer_radius, depth):
        """
        Perform calculations for the cylindrical annulus problem.

        Parameters:
            inner_radius (float): Inner radius of the annulus (cm).
            outer_radius (float): Outer radius of the annulus (cm).
            depth (float): Depth of the annulus (cm).

        Returns:
            tuple: Circulation (C), average vorticity (zeta), average divergence (div_mean),
                   average vertical velocity at the top of the annulus (w_mean).
        """
        import math

        # Radial and tangential velocity functions
        def radial_velocity(r):
            return 7 - 0.2 * r

        def tangential_velocity(r):
            return 40 + 2 * r

        # Compute circulation (C)
        v_inner = tangential_velocity(inner_radius)
        v_outer = tangential_velocity(outer_radius)
        C = 2 * math.pi * (outer_radius * v_outer - inner_radius * v_inner)

        # Compute average vorticity (zeta)
        area = math.pi * (outer_radius**2 - inner_radius**2)
        zeta = C / area

        # Compute average divergence (div_mean)
        u_inner = radial_velocity(inner_radius)
        u_outer = radial_velocity(outer_radius)
        div_mean = (2 * math.pi * (outer_radius * u_outer - inner_radius * u_inner)) / area

        # Compute average vertical velocity at the top of the annulus (w_mean)
        w_mean = -depth * div_mean

        return NestedAnswer({"a" : Answer(C, "cm^2/s", 0),
                             "b" : Answer(zeta, "s^-1", 2),
                             "c" : Answer(div_mean, "s^-1", 4),
                             "d" : Answer(w_mean, "cm/s", 4)})


if __name__ == '__main__':
    q = Question64(unique_id="q")
    print(q.question())
    print(q.answer())