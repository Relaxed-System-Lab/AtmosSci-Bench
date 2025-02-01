import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question61(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Physical Oceanography"
        self.template = """ 
By how much does the relative vorticity change for a column of fluid in a rotating cylinder if the column is moved 
from the center of the tank to a distance {distance_from_center_cm} cm from the center? The tank is rotating at 
the rate of {rotation_rate_rpm} revolutions per minute, the depth of the fluid at the center is {initial_depth_cm} cm, 
and the fluid is initially in solid-body rotation
        """
        self.func = self.calculate_relative_vorticity_change

        self.default_variables = {
            "rotation_rate_rpm": 20,         # Tank's rotation rate (RPM)
            "initial_depth_cm": 10,         # Initial fluid depth at the center (cm)
            "distance_from_center_cm": 50,  # Distance from the center (cm)
        }
        self.constant = {
            "gravity_m_s2": 9.8             # Gravitational acceleration (m/s^2)
        }

        self.independent_variables = {
            "rotation_rate_rpm": {"min": 1, "max": 100, "granularity": 1},
            "initial_depth_cm": {"min": 1, "max": 50, "granularity": 0.1},
            "distance_from_center_cm": {"min": 1, "max": 100, "granularity": 0.1},
        }
        self.dependent_variables = {}
        self.choice_variables = {}
        self.custom_constraints = []

        super(Question61, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_relative_vorticity_change(rotation_rate_rpm, initial_depth_cm, distance_from_center_cm, gravity_m_s2):
        """
        Calculate the change in relative vorticity for a column of fluid in a rotating cylinder.

        Parameters:
        - rotation_rate_rpm (float): Rotation rate of the tank in revolutions per minute (RPM).
        - initial_depth_cm (float): Initial depth of the fluid at the center in centimeters.
        - distance_from_center_cm (float): Distance from the center to the new position in centimeters.
        - gravity_m_s2 (float): Gravitational acceleration in m/s^2.

        Returns:
        - float: The change in relative vorticity (zeta1) in s^-1.
        """
        # Convert rotation rate from RPM to radians per second
        omega = (rotation_rate_rpm * 2 * math.pi) / 60  # rad/s

        # Convert initial depth and distance from cm to meters
        initial_depth_m = initial_depth_cm / 100
        distance_from_center_m = distance_from_center_cm / 100

        # Calculate the new depth (H1) using the provided formula
        new_depth_m = initial_depth_m + (omega**2 * distance_from_center_m**2) / (2 * gravity_m_s2)

        # Calculate the change in relative vorticity (zeta1)
        relative_vorticity_change = ((new_depth_m - initial_depth_m) / initial_depth_m) * 2 * omega

        return Answer(relative_vorticity_change, "s^-1", 3)


if __name__ == '__main__':
    q = Question61(unique_id="q")
    print(q.question())
    print(q.answer())