import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question18(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
A cylindrical column of air at {latitude}°N with radius {initial_radius} km expands to {expansion_factor} times its original radius.
If the air is initially at rest, what is the mean tangential velocity at the perimeter after expansion?
        """
        self.func = self.calculate_mean_tangential_velocity
        self.default_variables = {
            "latitude": 30,  # Latitude in degrees
            "initial_radius": 100,  # Initial radius of the column (km)
            # "angular_velocity": 7.2921e-5,  # Earth's angular velocity in rad/s
            "expansion_factor": 2  # Factor by which the radius expands
        }
        self.constant = {
            "angular_velocity": 7.2921e-5,  # Earth's angular velocity in rad/s
        }
        self.independent_variables = {
            "latitude": {"min": -90, "max": 90, "granularity": 1},
            "initial_radius": {"min": 10, "max": 500, "granularity": 10},
            # "angular_velocity": {"min": 7e-5, "max": 8e-5, "granularity": 1e-6},
        }
        self.dependent_variables = {
            "expansion_factor": lambda vars: vars.get("expansion_factor", 2),
        }
        self.choice_variables = {}
        self.custom_constraints = [
            lambda vars, res: vars["latitude"] >= 0 and vars["latitude"] <= 90,
        ]

        super(Question18, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_mean_tangential_velocity(latitude, initial_radius, angular_velocity, expansion_factor):
        """
        Calculate the mean tangential velocity at the perimeter of a cylindrical column of air.

        Parameters:
        - latitude (float): Latitude in degrees.
        - initial_radius (float): Initial radius of the column (in km).
        - angular_velocity (float): Angular velocity of the Earth (in rad/s).
        - expansion_factor (float): Factor by which the radius expands.

        Returns:
        - float: Mean tangential velocity (in m/s).
        """
        # Convert latitude to radians
        lat_rad = math.radians(latitude)

        # Convert initial radius from km to meters
        initial_radius_m = initial_radius * 1_000

        # Compute the Coriolis parameter (2 * Omega * sin(phi))
        coriolis_param = 2 * angular_velocity * math.sin(lat_rad)

        # Calculate the initial and final areas
        A_initial = math.pi * initial_radius_m**2
        final_radius_m = expansion_factor * initial_radius_m
        A_final = math.pi * final_radius_m**2

        # Circulation theorem: C_final = 2 * Omega * sin(phi) * (A_initial - A_final) + C_initial
        # Assuming C_initial = 0 (initially at rest)
        C_final = coriolis_param * (A_initial - A_final)

        # Calculate mean tangential velocity: V = C_final / (2 * pi * r_final)
        mean_velocity = C_final / (2 * math.pi * final_radius_m)

        return Answer(mean_velocity, "m/s", 1)


if __name__ == '__main__':
    q = Question18(unique_id="q")
    print(q.question())
    print(q.answer())