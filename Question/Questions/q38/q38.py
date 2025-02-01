import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question38(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Physical Oceanography"
        self.template = """
Consider an ocean of uniform density {density} kg/m^3. The ocean surface, which is flat in the longitudinal direction, slopes linearly with latitude from h={h1} m above mean sea level (MSL) at {lat_1}° N to h={h2} m below MSL at {lat_2}° N. Using hydrostatic balance, find the pressure at depth {depth} m below MSL. Hence show that the latitudinal pressure gradient ∂p/∂y and the geostrophic flow are independent of depth. Determine the magnitude and direction of the geostrophic flow at {reference_lat}° N.
        """
        self.func = self.calculate_ocean_dynamics
        self.default_variables = {
            "density": 1000,        # kg/m^3
            "coriolis_parameter": 1.03e-4,  # s^-1
            "lat_1": 40,            # degrees N
            "lat_2": 50,            # degrees N
            "h1": 0.1,              # m
            "h2": 0.1,             # m
            "depth": 10,            # m
            "reference_lat": 45     # degrees N
        }

        self.constant = {
            # "lat_to_meters": 111e3,  # meters per degree latitude
            "gravity": 9.81,        # m/s^2
        }

        self.independent_variables = {
            "density": {"min": 900, "max": 1100, "granularity": 1},
            "gravity": {"min": 9.5, "max": 10.0, "granularity": 0.01},
            "coriolis_parameter": {"min": 1e-4, "max": 1.1e-4, "granularity": 1e-6},
            "h1": {"min": 0.0, "max": 1.0, "granularity": 0.01},
            "h2": {"min": 0.0, "max": 1.0, "granularity": 0.01},
            "depth": {"min": 0.0, "max": 100.0, "granularity": 0.1},
            "lat_1": {"min": 30, "max": 60, "granularity": 0.1}
        }

        self.dependent_variables = {
            "lat_2": lambda vars: vars["lat_1"] + random.uniform(5, 15),
            "reference_lat": lambda vars: (vars["lat_1"] + vars["lat_2"]) / 2
        }

        self.choice_variables = {
        }

        self.custom_constraints = [
            lambda vars, res: vars["h1"] > vars["h2"],
            lambda vars, res: vars["lat_1"] < vars["lat_2"]
        ]

        super(Question38, self).__init__(unique_id, seed, variables)



    @staticmethod
    def calculate_ocean_dynamics(density, gravity, coriolis_parameter, lat_1, lat_2, h1, h2, depth, reference_lat):
        """
        Calculates the pressure at a given depth, the latitudinal pressure gradient, and the geostrophic flow.

        Returns:
            tuple: (pressure_at_depth, latitudinal_pressure_gradient, geostrophic_flow)
        """
        # Convert latitudes to distances in meters
        lat_to_meters = 111e3  # meters per degree latitude
        delta_h = -1.0 * (h2 + h1)
        delta_lat = abs(lat_2 - lat_1) * lat_to_meters  # in meters
        slope = delta_h / delta_lat  # ∂h/∂y

        # Calculate pressure at depth
        surface_pressure = 101325  # Atmospheric pressure in Pa
        pressure_at_depth = surface_pressure + gravity * density * (depth + h1)

        # Latitudinal pressure gradient (independent of depth)
        lat_pressure_gradient = gravity * density * slope  # ∂p/∂y

        # Geostrophic flow
        geostrophic_flow = -(gravity / coriolis_parameter) * slope  # u

        # return NestedAnswer([Answer(pressure_at_depth, "Pa", 0), Answer(lat_pressure_gradient, "Pa/m", 0), Answer(geostrophic_flow, "m/s", 2)])
        return NestedAnswer({
            "pressure_at_depth": Answer(pressure_at_depth, "Pa", 0),
            "latitudinal_pressure_gradient": Answer(lat_pressure_gradient, "Pa/m", 10),
            "geostrophic_flow": Answer(geostrophic_flow, "m/s", 4)
        })


if __name__ == '__main__':
    q = Question38(unique_id="q")
    print(q.question())
    print(q.answer())