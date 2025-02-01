import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer

class Question34(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
(i) A typical hurricane at, say, {lat_hurricane} latitude may have low-level winds of {wind_speed} at a radius of {radius} km from its center: do you expect this flow to be geostrophic?
(ii) Two weather stations near {lat_stations} are {station_distance} km apart, one exactly to the northeast of the other. At both locations, the 500 hPa wind is exactly southerly at {wind_speed_southerly}. At the north-eastern station, the height of the 500 hPa surface is {height_ne} m; what is the height of this surface at the other station?
"""
        self.func = self.calculate_hurricane_analysis
        self.default_variables = {
            "lat_hurricane": 30,  # Latitude of the hurricane (degrees)
            "wind_speed": 50,  # Low-level wind speed of the hurricane (m/s)
            "radius": 50,  # Radius from the hurricane center (km)
            "omega": 7.27e-5,  # Angular velocity of Earth (s^-1)
            "lat_stations": 45,  # Latitude of the weather stations (degrees)
            "wind_speed_southerly": 30,  # Southerly wind speed at the stations (m/s)
            "height_ne": 5510,  # Height of 500 hPa surface at northeastern station (m)
            "station_distance": 400  # Distance between the two stations (km)
        }

        # Constants used in the calculations
        self.constant = {
            # "gravity_speed": 9.81,  # Gravitational acceleration (m/s^2)
            "omega": 7.27e-5,        # Angular velocity of Earth (s^-1)
            "g": 9.81,  # Gravitational acceleration (m/s^2)
        }

        # Independent variables that can be randomly generated
        self.independent_variables = {
            "lat_hurricane": {"min": 0, "max": 90, "granularity": 1},
            "lat_stations": {"min": 0, "max": 90, "granularity": 1},
            "wind_speed_southerly": {"min": 10, "max": 100, "granularity": 1},
            "station_distance": {"min": 10, "max": 1000, "granularity": 10},
        }

        # Dependent variables calculated based on independent variables
        self.dependent_variables = {
            "height_ne": lambda vars: 5000 + 100 * (vars["lat_stations"] / 45)
        }

        # Choice variables for grouped related variable sets
        self.choice_variables = {
            "hemisphere": [
                # Northern Hemisphere, low latitude
                {"lat_hurricane": 15, "lat_stations": 30, "wind_speed": 40, "radius": 30},
                {"lat_hurricane": 20, "lat_stations": 35, "wind_speed": 45, "radius": 40},
                # Northern Hemisphere, mid latitude
                {"lat_hurricane": 30, "lat_stations": 45, "wind_speed": 50, "radius": 50},
                {"lat_hurricane": 35, "lat_stations": 50, "wind_speed": 60, "radius": 60},
                # Southern Hemisphere, low latitude
                {"lat_hurricane": -15, "lat_stations": -30, "wind_speed": 40, "radius": 30},
                {"lat_hurricane": -20, "lat_stations": -35, "wind_speed": 45, "radius": 40},
                # Southern Hemisphere, mid latitude
                {"lat_hurricane": -30, "lat_stations": -45, "wind_speed": 50, "radius": 50},
                {"lat_hurricane": -35, "lat_stations": -50, "wind_speed": 60, "radius": 60},
                # Polar regions
                {"lat_hurricane": 80, "lat_stations": 85, "wind_speed": 20, "radius": 100},
                {"lat_hurricane": -80, "lat_stations": -85, "wind_speed": 20, "radius": 100},
            ]
        }

        # Custom constraints to validate relationships between variables
        self.custom_constraints = [
            lambda vars, res: vars["lat_hurricane"] >= 0 and vars["lat_hurricane"] <= 90,
            lambda vars, res: vars["station_distance"] > 0
        ]

        super(Question34, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_hurricane_analysis(lat_hurricane, wind_speed, radius, lat_stations, wind_speed_southerly, height_ne, station_distance, omega, g):
        """
        Calculate Rossby number for hurricane and height at the other station.
        """
        # Part (i): Calculate Rossby number
        f_hurricane = 2 * omega * math.sin(math.radians(lat_hurricane))
        rossby_number = wind_speed / (f_hurricane * (radius * 1000))  # Convert radius to meters

        # Part (ii): Calculate height difference between stations
        f_stations = 2 * omega * math.sin(math.radians(lat_stations))
        dz_dx = (f_stations * wind_speed_southerly) / g
        delta_x = (station_distance * 1000) / math.sqrt(2)  # Convert km to m
        delta_z = dz_dx * delta_x
        height_west = height_ne - delta_z

        return NestedAnswer({"(i)": Answer(rossby_number, "", 1), "(ii)": Answer(height_west, "m", 0)})


if __name__ == '__main__':
    q = Question34(unique_id="q")
    print(q.question())
    print(q.answer())