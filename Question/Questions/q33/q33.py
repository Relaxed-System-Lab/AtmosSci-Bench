import random, math
from ..question import Question

class Question33(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """ 
What is the value of the centrifugal acceleration of a particle fixed to the earth at the equator and how does it compare to {g} m/s^2? 
What is the deviation of a plumb line from the true direction to the centre of the earth at {latitude}°N?
        """
        self.func = self.calculate_earth_parameters
        self.default_variables = {
            "rotation_rate": 7.27e-5,  # Earth's rotation rate in rad/s
            "earth_radius": 6370e3,  # Earth's radius in meters
            "g": 9.8,  # Gravitational acceleration in m/s^2
            "latitude": 45.0,  # Latitude in degrees
        }

        self.constant = {
            "pi": 3.14159  # Mathematical constant
        }

        self.independent_variables = {
            "rotation_rate": {"min": 6.5e-5, "max": 8e-5, "granularity": 1e-7},
            "earth_radius": {"min": 6.3e6, "max": 6.4e6, "granularity": 1e3},
            "g": {"min": 9.7, "max": 9.9, "granularity": 0.01},
            "latitude": {"min": 0, "max": 90, "granularity": 1},
        }

        self.dependent_variables = {
            # Latitude-dependent radius from Earth's center to the axis of rotation
            "r_latitude": lambda vars: vars["earth_radius"] * math.cos(math.radians(vars["latitude"])),
        }

        self.choice_variables = {
            # None for this problem as there are no grouped choice variables
        }

        self.custom_constraints = [
            # Rotation rate must always be positive
            lambda vars, res: vars["rotation_rate"] > 0,
        ]


        super(Question33, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_earth_parameters(rotation_rate, earth_radius, g, latitude):
        """
        Calculates centrifugal acceleration at the equator and at a specified latitude,
        compares it to gravity, and calculates the deviation of a plumb line.
        """
        # Centrifugal acceleration at the equator
        centrifugal_acceleration_equator = rotation_rate**2 * earth_radius

        # Ratio to gravity
        ratio_to_gravity = centrifugal_acceleration_equator / g

        # Distance to rotation axis at the specified latitude
        r_latitude = earth_radius * math.cos(math.radians(latitude))

        # Centrifugal acceleration at the specified latitude
        centrifugal_acceleration_latitude = rotation_rate**2 * r_latitude

        # Vertical and horizontal components at the latitude
        vertical_component = centrifugal_acceleration_latitude * math.cos(math.radians(latitude))
        horizontal_component = centrifugal_acceleration_latitude * math.sin(math.radians(latitude))

        # Deviation angle calculation
        tan_gamma = horizontal_component / (g - vertical_component)
        deviation_angle_rad = tan_gamma  # Using small angle approximation
        deviation_angle_deg = math.degrees(deviation_angle_rad)

        return {
            "centrifugal_acceleration_equator": centrifugal_acceleration_equator,
            "ratio_to_gravity": ratio_to_gravity,
            "deviation_angle_rad": deviation_angle_rad,
            "deviation_angle_deg": deviation_angle_deg,
        }


if __name__ == '__main__':
    q = Question33(unique_id="q")
    print(q.question())
    print(q.answer())