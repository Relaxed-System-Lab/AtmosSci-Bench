import random, math
from ..question import Question
from Questions.answer import Answer


class Question15(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """ An aircraft flying a heading of {air_heading}° (i.e., {air_heading}° to the east of north) at air speed {air_speed} m/s moves relative to the ground due east (90°) at {ground_speed} m/s. If the plane is flying at constant pressure, what is its rate of change in altitude (in meters per kilometer horizontal distance) assuming a steady pressure field, geostrophic winds, and f={f} s^-1 ? """
        self.func = self.calculate_rate_of_change_in_altitude
        self.default_variables = {
            "air_speed": 200,  # Airspeed of the aircraft in m/s
            "air_heading": 60,  # Aircraft heading in degrees (0 degrees is north)
            "ground_speed": 225,  # Ground speed of the aircraft in m/s
            "f": 1e-4,  # Coriolis parameter in s^-1
        }

        self.constant = {
            "g": 9.8,  # Gravitational acceleration in m/s^2
            "ground_heading": 90,  # Ground heading in degrees (eastward)
        }

        self.independent_variables = {
            "air_speed": {"min": 100, "max": 300, "granularity": 1},
            "air_heading": {"min": 0, "max": 90, "granularity": 1},
            "ground_speed": {"min": 0, "max": 500, "granularity": 1},
        #   "ground_heading": {"min": 0, "max": 360, "granularity": 1},
            "f": {"min": 1e-5, "max": 1.5e-4, "granularity": 1e-5}
        #   "g": {"min": 9.7, "max": 9.9, "granularity": 0.01}
        }

        self.dependent_variables = {}

        self.choice_variables  = {
            "wind_conditions": [
                {"air_speed": 200, "ground_speed": 225},
                {"air_speed": 150, "ground_speed": 180},
                {"air_speed": 250, "ground_speed": 275}
            ]
        }

        self.custom_constraints = [
            lambda vars, res: vars["air_speed"] >= 0,
            lambda vars, res: vars["ground_speed"] >= 0
        ]
        super(Question15, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_rate_of_change_in_altitude(air_speed, air_heading, ground_speed, ground_heading, f, g):
        """
        Calculate the rate of change in altitude in meters per kilometer horizontal distance.

        Parameters:
            air_speed (float): Airspeed of the aircraft in m/s.
            air_heading (float): Aircraft heading in degrees (0 degrees is north).
            ground_speed (float): Ground speed of the aircraft in m/s (direction is assumed).
            ground_heading (float): Ground heading in degrees (0 degrees is north).
            f (float): Coriolis parameter in s^-1.
            g (float): Gravitational acceleration in m/s^2.

        Returns:
            float: Rate of change in altitude in meters per kilometer.
        """
        import math

        # Convert headings to radians
        air_heading_rad = math.radians(air_heading)
        ground_heading_rad = math.radians(ground_heading)

        # Resolve air velocity components in the x (east) and y (north) directions
        air_velocity_x = air_speed * math.sin(air_heading_rad)  # East component
        air_velocity_y = air_speed * math.cos(air_heading_rad)  # North component

        # Resolve ground velocity components in the x (east) and y (north) directions
        ground_velocity_x = ground_speed * math.sin(ground_heading_rad)  # East component
        ground_velocity_y = ground_speed * math.cos(ground_heading_rad)  # North component

        # Calculate wind velocity (relative to the ground)
        wind_velocity_x = ground_velocity_x - air_velocity_x
        wind_velocity_y = ground_velocity_y - air_velocity_y

        # Calculate geostrophic wind component in the northward direction (vg)
        vg = wind_velocity_y

        # Calculate the rate of change of altitude per horizontal distance
        rate_of_change = (f * vg) / g

        # Convert to meters per kilometer
        rate_of_change_m_per_km = rate_of_change * 1000

        return Answer(rate_of_change_m_per_km, "m/km", 2)


if __name__ == '__main__':
    q = Question15(unique_id="q")
    print(q.question())
    print(q.answer())