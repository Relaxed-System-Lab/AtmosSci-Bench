import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question89(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Physical Oceanography"
        self.template = """A submarine that is neutrally buoyant and stationary is submerged at a depth of {depth_m} m at a latitude of {latitude_deg}°. Upon hearing an unusual noise to the east, the SONAR operator alerts the captain, who chooses to investigate. With an easterly speed of {speed_east_ms} m/s, how much time will pass before the submarine reaches the surface if no adjustments are made to the controls?"""

        self.func = self.time_to_surface_due_to_coriolis

        self.default_variables = {
            "depth_m": 100.0,
            "speed_east_ms": 10.0,
            "latitude_deg": 30.0,
        }

        self.constant = {
            # "omega_earth": 7.29e-5  # Earth's angular velocity (rad/s)
        }

        self.independent_variables = {
            "depth_m": {"min": 10.0, "max": 1000.0, "granularity": 1.0},
            "speed_east_ms": {"min": 0.1, "max": 50.0, "granularity": 0.1},
            "latitude_deg": {"min": 0.0, "max": 90.0, "granularity": 0.1},
        }

        self.dependent_variables = {
            # No dependent variables needed in this case
        }

        self.choice_variables = {
            # No specific choice-based groups for this question
        }

        self.custom_constraints = [
            lambda vars, res: res > 0,  # Time to surface must be positive
        ]

        super(Question89, self).__init__(unique_id, seed, variables)

    @staticmethod
    def time_to_surface_due_to_coriolis(depth_m, speed_east_ms, latitude_deg):
        """
        Calculate the time for a neutrally buoyant submarine to reach the surface 
        due to vertical Coriolis acceleration.

        Parameters:
        - depth_m (float): Depth of the submarine in meters.
        - speed_east_ms (float): Submarine's speed toward the east in m/s.
        - latitude_deg (float): Latitude in degrees.

        Returns:
        - float: Time in seconds for the submarine to reach the surface.
        """
        import math

        omega_earth = 7.29e-5  # Earth's angular velocity in rad/s
        latitude_rad = math.radians(latitude_deg)

        # Calculate vertical Coriolis acceleration: a = 2 * omega * u * cos(latitude)
        vertical_accel = 2 * omega_earth * speed_east_ms * math.cos(latitude_rad)

        if vertical_accel <= 0:
            raise ValueError("Vertical Coriolis acceleration must be positive to reach the surface.")

        # Use kinematic equation: s = 0.5 * a * t^2 => t = sqrt(2 * s / a)
        time_seconds = math.sqrt(2 * depth_m / vertical_accel)

        return Answer(time_seconds, "s", 3)


if __name__ == '__main__':
    q = Question89(unique_id="q")
    print(q.question())
    print(q.answer())