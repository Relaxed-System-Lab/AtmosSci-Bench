import random, math
from ..question import Question
from Questions.answer import Answer


class Question19(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
An air parcel at {lat_initial}°N moves northward, conserving absolute vorticity. If its initial relative vorticity is {rel_vorticity_initial} s^-1, 
what is its relative vorticity upon reaching {lat_final}°N
        """
        self.func = self.calculate_relative_vorticity
        self.default_variables = {
            "lat_initial": 30.0,  # Initial latitude in degrees
            "lat_final": 90.0,    # Final latitude in degrees
            "rel_vorticity_initial": 5e-5  # Initial relative vorticity in s^-1
        }

        self.independent_variables = {
            "lat_initial": {"min": -90.0, "max": 90.0, "granularity": 1},
            "lat_final": {"min": -90.0, "max": 90.0, "granularity": 1},
            "rel_vorticity_initial": {"min": -1e-4, "max": 1e-4, "granularity": 1e-6}
        }
        self.dependent_variables = {}
        self.choice_variables = {}
        self.custom_constraints = [
            lambda vars, res: -90.0 <= vars["lat_initial"] <= 90.0,
            lambda vars, res: -90.0 <= vars["lat_final"] <= 90.0
        ]

        super(Question19, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_relative_vorticity(lat_initial, lat_final, rel_vorticity_initial):
        """
        Calculate the relative vorticity of an air parcel conserving absolute vorticity.

        Parameters:
            lat_initial (float): Initial latitude in degrees.
            lat_final (float): Final latitude in degrees.
            rel_vorticity_initial (float): Initial relative vorticity (zeta_initial) in s^-1.

        Returns:
            float: Final relative vorticity (zeta_final) in s^-1.
        """
        omega = 7.2921e-5  # Earth's angular velocity in s^-1

        # Convert latitudes from degrees to radians
        lat_initial_rad = math.radians(lat_initial)
        lat_final_rad = math.radians(lat_final)

        # Calculate Coriolis parameters
        f_initial = 2 * omega * math.sin(lat_initial_rad)
        f_final = 2 * omega * math.sin(lat_final_rad)

        # Calculate final relative vorticity
        rel_vorticity_final = rel_vorticity_initial + (f_initial - f_final)

        return Answer(rel_vorticity_final, "s^-1", 6)



if __name__ == '__main__':
    q = Question19(unique_id="q")
    print(q.question())
    print(q.answer())