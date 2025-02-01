import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question57(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "TBD"
        self.template = """ 
        The following wind data were received from {distance} km to the east, north, west, and south of a station, respectively:
        {east_wind_direction}°, {east_wind_speed} m/s; 
        {north_wind_direction}°, {north_wind_speed} m/s; 
        {west_wind_direction}°, {west_wind_speed} m/s; 
        {south_wind_direction}°, {south_wind_speed} m/s. 

        Calculate the approximate horizontal divergence at the station.
        """
        self.func = self.calculate_horizontal_divergence
        self.default_variables = {
            "east_wind_speed": 10,
            "east_wind_direction": 90,
            "north_wind_speed": 4,
            "north_wind_direction": 120,
            "west_wind_speed": 8,
            "west_wind_direction": 90,
            "south_wind_speed": 4,
            "south_wind_direction": 60,
            "distance": 50
        }

        self.constant = {}

        self.independent_variables = {
            "east_wind_speed": {"min": 0, "max": 20, "granularity": 0.1},
            "north_wind_speed": {"min": 0, "max": 20, "granularity": 0.1},
            "west_wind_speed": {"min": 0, "max": 20, "granularity": 0.1},
            "south_wind_speed": {"min": 0, "max": 20, "granularity": 0.1},
            "distance": {"min": 10, "max": 100, "granularity": 1}
        }

        self.dependent_variables = {
            "east_wind_direction": lambda vars: vars["east_wind_speed"] * 9,  # Example, adjustable
            "north_wind_direction": lambda vars: vars["north_wind_speed"] * 10,
            "west_wind_direction": lambda vars: vars["west_wind_speed"] * 9,
            "south_wind_direction": lambda vars: vars["south_wind_speed"] * 15
        }

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["distance"] > 0  # Ensure the distance is positive
        ]

        super(Question57, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_horizontal_divergence(
        east_wind_speed, east_wind_direction,
        north_wind_speed, north_wind_direction,
        west_wind_speed, west_wind_direction,
        south_wind_speed, south_wind_direction,
        distance
    ):
        """
        Calculate the horizontal divergence at a station based on wind data.

        Parameters:
        - east_wind_speed: Wind speed at the east point (m/s)
        - east_wind_direction: Wind direction at the east point (degrees)
        - north_wind_speed: Wind speed at the north point (m/s)
        - north_wind_direction: Wind direction at the north point (degrees)
        - west_wind_speed: Wind speed at the west point (m/s)
        - west_wind_direction: Wind direction at the west point (degrees)
        - south_wind_speed: Wind speed at the south point (m/s)
        - south_wind_direction: Wind direction at the south point (degrees)
        - distance: Distance between the station and cardinal points (km)

        Returns:
        - Horizontal divergence (1/s)
        """
        # Convert distance from km to meters
        delta = distance * 1000

        # print("=======")
        # Convert wind directions to radians
        east_rad = math.radians(east_wind_direction)
        north_rad = math.radians(north_wind_direction)
        west_rad = math.radians(west_wind_direction)
        south_rad = math.radians(south_wind_direction)
        
        # print("east_rad: ", east_rad)
        # print("north_rad: ", north_rad)
        # print("west_rad: ", west_rad)
        # print("south_rad: ", south_rad)

        # Calculate u (zonal component) and v (meridional component) for each point
        u_east = east_wind_speed * math.cos(east_rad)
        v_east = east_wind_speed * math.sin(east_rad)

        u_north = north_wind_speed * math.cos(north_rad)
        v_north = north_wind_speed * math.sin(north_rad)

        u_west = west_wind_speed * math.cos(west_rad)
        v_west = west_wind_speed * math.sin(west_rad)

        u_south = south_wind_speed * math.cos(south_rad)
        v_south = south_wind_speed * math.sin(south_rad)

        # Calculate finite differences
        # print("u_east: ", u_east)
        # print("u_west: ", u_west)
        # print("v_north: ", v_north)
        # print("v_south: ", v_south)
        du_dx = (u_east - u_west) / (2 * delta)
        dv_dy = (v_north - v_south) / (2 * delta)

        # Calculate horizontal divergence
        divergence = du_dx + dv_dy

        return divergence


if __name__ == '__main__':
    q = Question57(unique_id="q")
    print(q.question())
    print(q.answer())