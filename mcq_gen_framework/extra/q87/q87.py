import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question87(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Physical Oceanography"
        self.template = """In midlatitude regions, Kelvin waves travel along coastlines.

a. Which direction (north or south) do these waves travel if they move along the {coast_name}?

b. Compute the Rossby deformation radius for such a wave at {latitude_deg}°.

c. Find the time τ required for a Kelvin wave to travel a distance of {distance_km} km.

Assume a Kelvin wave is moving through a water layer with a thickness of H₀={H0} m."""
        
        self.func = self.calculate_kelvin_wave_properties
        
        self.default_variables = {
            "hemisphere": "northern",
            "coast_orientation": "west",
            "coast_name": "European Atlantic coast",
            "latitude_deg": 45.0,
            "H0": 1000.0,
            "distance_km": 1000.0
        }

        self.constant = {
            # "g": 9.81,  # gravitational acceleration (m/s^2)
            # "omega": 7.2921e-5  # Earth's angular velocity (rad/s)
        }

        self.independent_variables = {
            "latitude_deg": {"min": 0, "max": 90, "granularity": 0.1},
            "H0": {"min": 10, "max": 5000, "granularity": 10},
            "distance_km": {"min": 10, "max": 10000, "granularity": 10},
        }

        self.dependent_variables = {
            "coast_orientation": lambda vars: "west" if vars["latitude_deg"] > 0 else "east",
            "hemisphere": lambda vars: "northern" if vars["latitude_deg"] >= 0 else "southern",
        }

        self.choice_variables = {
            "coast": [
                {"coast_name": "European Atlantic coast", "coast_orientation": "west"},
                {"coast_name": "Chilean Pacific coast", "coast_orientation": "east"},
                {"coast_name": "East African coast", "coast_orientation": "west"},
                {"coast_name": "Australian east coast", "coast_orientation": "east"}
            ]
        }

        self.custom_constraints = [
            lambda vars, res: 0 <= vars["latitude_deg"] <= 90,
            lambda vars, res: vars["H0"] > 0,
            lambda vars, res: vars["distance_km"] > 0
        ]

        super(Question87, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_kelvin_wave_properties(hemisphere, coast_orientation, coast_name, latitude_deg, H0, distance_km):
        """
        Calculate:
        a) Direction of wave propagation along coast (e.g., 'north')
        b) Rossby deformation radius (m)
        c) Time to propagate a given distance (s)
        """
        import math
        
        # Part (a): Determine propagation direction
        if hemisphere.lower() == "northern":
            direction = "north" if coast_orientation.lower() == "west" else "south"
        else:
            direction = "south" if coast_orientation.lower() == "west" else "north"
        
        # Constants
        g = 9.81  # m/s^2
        omega = 7.2921e-5  # rad/s

        # Latitude in radians
        latitude_rad = math.radians(latitude_deg)
        
        # Coriolis parameter
        f = 2 * omega * math.sin(latitude_rad)
        
        # Rossby deformation radius
        RD = math.sqrt(g * H0) / f
        
        # Propagation speed
        c = math.sqrt(g * H0)
        
        # Convert distance to meters
        distance_m = distance_km * 1000
        
        # Time τ
        tau = distance_m / c
        
        return NestedAnswer({
            "direction": Answer(direction, "", 0),
            "Rossby_deformation_radius": Answer(RD, "m", 2),
            "time_to_propagate": Answer(tau, "s", 2)
        })


if __name__ == '__main__':
    q = Question87(unique_id="q")
    print(q.question())
    print(q.answer())