import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question39(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
If a baseball player throws a ball a horizontal distance of {horizontal_distance} m at {latitude}° latitude in {time} s, by how much is it deflected laterally as a result of the rotation of Earth?
        """
        self.func = self.calculate_lateral_deflection
        self.default_variables = {
            "horizontal_distance": 100.0,  # meters
            "time": 4.0,  # seconds
            "latitude": 30.0,  # degrees
        }

        self.constant = {
            "omega": 7.292e-5,  # Earth's angular velocity in radians per second
        }

        self.independent_variables = {
            "horizontal_distance": {"min": 10.0, "max": 1000.0, "granularity": 1.0},
            "time": {"min": 1.0, "max": 10.0, "granularity": 0.1},
            "latitude": {"min": -90.0, "max": 90.0, "granularity": 0.1},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = []


        super(Question39, self).__init__(unique_id, seed, variables)



    @staticmethod
    def calculate_lateral_deflection(horizontal_distance, time, latitude, omega=7.292e-5):
        """
        Calculate the lateral deflection of a ball due to Earth's rotation.

        Parameters:
            horizontal_distance (float): Horizontal distance the ball travels (in meters).
            time (float): Time it takes for the ball to travel the distance (in seconds).
            latitude (float): Latitude where the ball is thrown (in degrees).
            omega (float): Earth's angular velocity (in radians per second). Default is 7.292e-5.

        Returns:
            float: Lateral deflection of the ball (in meters).
        """
        # Use sin(latitude) = 0.5 explicitly for 30° latitude
        sin_latitude = 0.5 if latitude == 30 else math.sin(math.radians(latitude))

        # Compute the lateral deflection using the formula y = -omega * x * t * sin(latitude) / 2
        # deflection = -omega * horizontal_distance * time * sin_latitude / 2
        deflection = -omega * horizontal_distance * time * sin_latitude

        deflection_in_cm = deflection * 100

        return Answer(deflection_in_cm, "cm", 3)



if __name__ == '__main__':
    q = Question39(unique_id="q")
    print(q.question())
    print(q.answer())