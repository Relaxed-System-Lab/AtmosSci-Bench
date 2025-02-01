import random, math
from ..question import Question
from Questions.answer import Answer


class Question14(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
The temperature at a point {distance} km north of a station is {temp_difference} °C cooler than at the station. If the wind is blowing from the {wind_direction} at {wind_speed} m/s and the air is being heated by radiation at the rate of {radiation_heating} °C/h, what is the local temperature change at the station?
        """
        self.func = self.calculate_local_temperature_change
        self.default_variables = {
            "temp_difference": 3.0,  # Temperature difference in degrees Celsius
            "wind_direction": "northeast",  # Wind direction as a string
            "wind_speed": 20.0,  # Wind speed in m/s
            "radiation_heating": 1.0,  # Heating rate in degrees Celsius per hour
            "distance": 50000.0  # Distance in meters (50 km)
        }
        self.independent_variables = {
            "temp_difference": {"min": 0.1, "max": 10.0, "granularity": 0.1},
            "wind_speed": {"min": 1.0, "max": 50.0, "granularity": 0.1},
            "radiation_heating": {"min": 0.1, "max": 5.0, "granularity": 0.1},
            "distance": {"min": 1000.0, "max": 100000.0, "granularity": 1000.0}
        }

        self.dependent_variables = {}
        self.choice_variables = {
            "wind": [
                {"wind_direction": "northeast"},
                {"wind_direction": "northwest"},
                {"wind_direction": "southeast"},
                {"wind_direction": "southwest"}
            ]
        }
        self.custom_constraints = [
            lambda vars, res: vars["distance"] > 0
        ]

        super(Question14, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_local_temperature_change(temp_difference, wind_direction, wind_speed, radiation_heating, distance):
        """
        Calculate the local temperature change at a station.

        Parameters:
            temp_difference (float): Temperature difference (in degrees C).
            wind_direction (str): Wind direction (e.g., 'northeast').
            wind_speed (float): Wind speed (in m/s).
            radiation_heating (float): Heating rate (in degrees C per hour).
            distance (float): Distance between locations (in meters).

        Returns:
            float: Local temperature change (in degrees C per hour).
        """
        # Get angle for wind direction
        wind_angle = next(
            item["angle"] for item in [
                {"direction": "northeast", "angle": 45.0},
                {"direction": "northwest", "angle": 135.0},
                {"direction": "southeast", "angle": -45.0},
                {"direction": "southwest", "angle": -135.0}
            ] if item["direction"] == wind_direction
        )
        # Convert angle to radians
        wind_angle_rad = math.radians(wind_angle)

        # Calculate the temperature gradient
        temp_gradient = temp_difference / distance

        # Calculate the advection term (V ⋅ ∇T)
        advection = wind_speed * temp_gradient * math.cos(wind_angle_rad)

        # Convert advection to degrees C per hour
        advection_per_hour = advection * 3600  # seconds to hours

        # Calculate the local temperature change
        local_temp_change = radiation_heating - advection_per_hour

        return Answer(local_temp_change, "°C/h", 3)


if __name__ == '__main__':
    q = Question14(unique_id="q")
    print(q.question())
    print(q.answer())