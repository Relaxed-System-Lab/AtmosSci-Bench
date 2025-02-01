import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question20(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
An air column at {initial_lat}°N with ζ={initial_relative_vorticity} initially stretches from the surface to a fixed tropopause at {initial_height} km height. 
If the air column moves until it is over a mountain barrier {barrier_height} km high at {final_lat}°N,
what are its absolute vorticity and relative vorticity as it passes the mountaintop, assuming that the flow satisfies the barotropic potential vorticity equation?
        """

        self.func = self.calculate_vorticity
        self.default_variables = {
            "initial_lat": 60,  # Initial latitude in degrees
            "final_lat": 45,    # Final latitude in degrees
            "initial_height": 10.0,  # Initial height in km
            "final_height": 7.5,     # Final height in km (initial_height - barrier_height)
            "barrier_height": 2.5,   # Mountain barrier height in km
            "initial_relative_vorticity": 0  # Initial relative vorticity in s^-1
        }
        self.independent_variables = {
            "initial_lat": {"min": 0, "max": 90, "granularity": 1},
            "final_lat": {"min": 0, "max": 90, "granularity": 1},
            "initial_height": {"min": 5.0, "max": 20.0, "granularity": 0.1},
            "barrier_height": {"min": 0.1, "max": 5.0, "granularity": 0.1},
            "initial_relative_vorticity": {"min": -1e-5, "max": 1e-5, "granularity": 1e-6}
        }
        self.dependent_variables = {
            "final_height": lambda vars: vars["initial_height"] - vars["barrier_height"]
        }
        self.choice_variables = {}
        self.custom_constraints = [
            lambda vars, res: vars["initial_height"] > vars["barrier_height"]
        ]


        super(Question20, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_vorticity(initial_lat, final_lat, initial_height, final_height, barrier_height, initial_relative_vorticity):
        """
        Calculate the absolute and relative vorticity of an air column using the barotropic potential vorticity equation.

        Parameters:
            initial_lat (float): Initial latitude in degrees.
            final_lat (float): Final latitude in degrees.
            initial_height (float): Initial height of the air column in km.
            final_height (float): Final height of the air column in km.
            barrier_height (float): Height of the mountain barrier in km.
            initial_relative_vorticity (float): Initial relative vorticity (ζ) in s^-1.

        Returns:
            dict: A dictionary containing the absolute vorticity and relative vorticity in s^-1.
        """
        # Earth's rotation rate (rad/s)
        omega = 7.2921e-5

        # Calculate Coriolis parameter (f = 2 * omega * sin(latitude))
        def coriolis_parameter(latitude):
            return 2 * omega * math.sin(math.radians(latitude))

        # Initial and final Coriolis parameters
        f_initial = coriolis_parameter(initial_lat)
        f_final = coriolis_parameter(final_lat)

        # Conservation of potential vorticity: (ζ + f) / H = constant
        potential_vorticity_initial = (initial_relative_vorticity + f_initial) / initial_height
        absolute_vorticity_final = potential_vorticity_initial * final_height

        # Relative vorticity at the final state
        relative_vorticity_final = absolute_vorticity_final - f_final

        return NestedAnswer({
            "absolute_vorticity": Answer(absolute_vorticity_final, "s^-1", 8),
            "relative_vorticity": Answer(relative_vorticity_final, "s^-1", 8)
        })



if __name__ == '__main__':
    q = Question20(unique_id="q")
    print(q.question())
    print(q.answer())