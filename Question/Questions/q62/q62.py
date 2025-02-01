import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question62(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
A westerly zonal flow at {lat_start} degrees is forced to rise adiabatically over a north-south-oriented mountain barrier. 
Before striking the mountain, the westerly wind increases linearly toward the south at a rate of {vorticity_gradient} m/s per 1000 km. 
The crest of the mountain range is at {p_start} hPa, and the tropopause, located at {p_end} hPa, remains undisturbed. 
What is the initial relative vorticity of the air? What is its relative vorticity when it reaches the crest if it is deflected {lat_deflection} degrees latitude toward the south during the forced ascent?
If the current assumes a uniform speed of {wind_speed} m/s during its ascent to the crest, what is the radius of curvature of the streamlines at the crest?
        """
        self.func = self.calculate_vorticity_and_radius
        self.default_variables = {
            "lat_start": 45,  # Initial latitude in degrees
            "vorticity_gradient": 10,  # m/s per 1000 km
            "p_start": 800,  # Initial pressure level (hPa)
            "p_end": 300,  # Final pressure level (hPa)
            "wind_speed": 20,  # Uniform speed during ascent (m/s)
            "lat_deflection": 5,  # Latitude deflection in degrees
        }

        self.constant = {
            "omega": 7.2921e-5  # Earth's angular velocity (rad/s)
        }

        self.independent_variables = {
            "lat_start": {"min": 0, "max": 90, "granularity": 1},
            "vorticity_gradient": {"min": 0.1, "max": 50, "granularity": 0.1},
            "p_start": {"min": 500, "max": 1000, "granularity": 10},
            "p_end": {"min": 100, "max": 500, "granularity": 10},
            "wind_speed": {"min": 1, "max": 50, "granularity": 1},
        }

        self.dependent_variables = {
            "lat_deflection": lambda vars: vars["lat_start"] - 5,
        }

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["p_start"] > vars["p_end"],
            lambda vars, res: vars["lat_start"] > vars["lat_deflection"],
        ]
        super(Question62, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_vorticity_and_radius(lat_start, vorticity_gradient, p_start, p_end, wind_speed, lat_deflection, omega):
        """
        Calculate initial relative vorticity, vorticity at crest, and radius of curvature of streamlines.

        Parameters:
        lat_start (float): Initial latitude in degrees.
        vorticity_gradient (float): Rate of change of wind speed per distance (m/s per km).
        p_start (float): Initial pressure level (hPa).
        p_end (float): Final pressure level (hPa).
        wind_speed (float): Uniform speed during ascent (m/s).
        lat_deflection (float): Final latitude in degrees.
        omega (float): Earth's angular velocity (rad/s).

        Returns:
        dict: A dictionary with keys for initial relative vorticity, relative vorticity at crest, and radius of curvature (m).
        """
        import math

        # Convert latitudes to radians
        lat_start_rad = math.radians(lat_start)
        lat_end_rad = math.radians(lat_deflection)

        # Coriolis parameter (f) at initial and final latitudes
        f_start = 2 * omega * math.sin(lat_start_rad)
        f_end = 2 * omega * math.sin(lat_end_rad)

        # Initial relative vorticity (zeta_0)
        zeta_0 = -vorticity_gradient * 1e-6  # Convert gradient from per 1000 km to per meter

        # Pressure layer thickness
        delta_p_start = p_start
        delta_p_end = p_end

        # Apply potential vorticity conservation: (f0 + zeta0) / delta_p0 = (f1 + zeta1) / delta_p1
        zeta_1 = ((f_start + zeta_0) / delta_p_start) * delta_p_end - f_end

        # Radius of curvature (R) from vorticity at crest
        if zeta_1 != 0:
            radius_of_curvature = wind_speed / zeta_1
        else:
            radius_of_curvature = float('inf')  # Infinite radius for zero vorticity

        return NestedAnswer({
            "initial_relative_vorticity": Answer(zeta_0, "s^-1", 6),
            "relative_vorticity_at_crest": zeta_1,
            "radius_of_curvature": radius_of_curvature
        })



if __name__ == '__main__':
    q = Question62(unique_id="q")
    print(q.question())
    print(q.answer())