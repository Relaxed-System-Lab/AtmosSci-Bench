import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question63(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
(a) How far must a zonal ring of air initially at rest with respect to Earth's surface at {latitude_deg}° latitude 
and {initial_height_km} km height be displaced latitudinally in order to acquire an easterly (east to west) component 
of {target_velocity_m_s} m/s with respect to Earth's surface? 
(b) To what height must it be displaced vertically in order to acquire the same velocity? 
Assume a frictionless atmosphere.
        """
        self.func = self.calculate_displacement

        self.default_variables = {
            "latitude_deg": 60.0,  # Latitude in degrees
            "initial_height_km": 100.0,  # Initial height in kilometers
            "target_velocity_m_s": 10.0  # Target zonal velocity in m/s
        }

        self.constant = {
            "earth_angular_velocity": 7.2921e-5,  # Angular velocity of Earth in rad/s
            "earth_radius_km": 6371.0  # Radius of Earth in kilometers
        }

        self.independent_variables = {
            "latitude_deg": {"min": 0, "max": 90, "granularity": 1.0},
            "initial_height_km": {"min": 0, "max": 500, "granularity": 1.0},
            "target_velocity_m_s": {"min": 0, "max": 100, "granularity": 1.0}
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: -90 <= vars["latitude_deg"] <= 90
        ]

        super(Question63, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_displacement(latitude_deg, initial_height_km, target_velocity_m_s, earth_angular_velocity, earth_radius_km):
        """
        Calculate latitudinal and vertical displacement to acquire a target velocity.

        Parameters:
        - latitude_deg (float): Latitude in degrees.
        - initial_height_km (float): Initial height in kilometers.
        - target_velocity_m_s (float): Target zonal velocity in m/s.

        Returns:
        - tuple: (latitudinal_displacement_km, vertical_displacement_km)
        """
        import math

        # Convert latitude to radians
        latitude_rad = math.radians(latitude_deg)

        # Calculate delta R due to target velocity and angular momentum conservation
        delta_r = -target_velocity_m_s / (2 * earth_angular_velocity)

        # Calculate latitudinal displacement (negative direction toward equator)
        delta_y = delta_r / math.sin(latitude_rad)
        if latitude_deg > 0:  # Ensure equatorward displacement is negative in the northern hemisphere
            delta_y = -abs(delta_y)

        # Calculate vertical displacement (should remain positive for upward motion)
        delta_z = abs(delta_r / math.cos(latitude_rad))

        delta_y_in_km = delta_y / 1000
        delta_z_in_km = delta_z / 1000

        return NestedAnswer({"(a)": Answer(delta_y_in_km, "km", 1), "(b)": Answer(delta_z_in_km, "km", 1)})


if __name__ == '__main__':
    q = Question63(unique_id="q")
    print(q.question())
    print(q.answer())