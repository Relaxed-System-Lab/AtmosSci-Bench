import random, math
from ..question import Question
from Questions.answer import Answer

class Question13(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
A ship is steaming northward at a rate of {ship_velocity_kmh} km/h. The surface pressure increases toward the northwest 
at a rate of {pressure_gradient_pakm} Pa/km. What is the pressure tendency recorded at a nearby island station if the 
pressure aboard the ship decreases at a rate of {pressure_change_pah} Pa/h?
        """
        self.func = self.calculate_pressure_tendency
        self.default_variables = {
            "ship_velocity_kmh": 10,  # km/h
            "pressure_gradient_pakm": 5,  # Pa/km
            "pressure_change_pah": 100 / 3,  # Pa/h
        #    "angle_degrees": 45  # degrees
        }

        self.constant = {
            "angle_degrees": 45  # degrees
        }

        self.independent_variables = {
            "ship_velocity_kmh": {"min": 0, "max": 100, "granularity": 0.1},
            "pressure_gradient_pakm": {"min": 0, "max": 100, "granularity": 0.1},
            "pressure_change_pah": {"min": -1000, "max": 1000, "granularity": 0.1},
        #    "angle_degrees": {"min": 0, "max": 180, "granularity": 0.1}
        }


        self.dependent_variables = {}

        self.choice_variables= {}
        self.custom_constraints = [
            lambda vars, res: vars["pressure_change_pah"] <= 0  # Pressure change aboard the ship should be non-positive
        ]
        super(Question13, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_pressure_tendency(ship_velocity_kmh, pressure_gradient_pakm, pressure_change_pah, angle_degrees):
        """
        Calculate the pressure tendency at a nearby island station.

        Parameters:
            ship_velocity_kmh (float): The velocity of the ship in km/h.
            pressure_gradient_pakm (float): The pressure gradient magnitude in Pa/km.
            pressure_change_pah (float): The rate of pressure change aboard the ship in Pa/h.
            angle_degrees (float): The angle between velocity and pressure gradient vectors in degrees.

        Returns:
            float: The pressure tendency recorded at the nearby island station in Pa/h.
        """
        # Convert angle from degrees to radians
        angle_radians = math.radians(angle_degrees)

        # Calculate the advection term: V * |grad(p)| * cos(angle)
        advection_term = ship_velocity_kmh * pressure_gradient_pakm * math.cos(angle_radians)

        # Calculate the pressure tendency
        pressure_tendency = -pressure_change_pah - advection_term

        return Answer(pressure_tendency, "Pa/h", 1)

if __name__ == '__main__':
    q = Question13(unique_id="q")
    print(q.question())
    print(q.answer())