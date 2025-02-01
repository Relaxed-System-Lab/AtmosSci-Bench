import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question46(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """
Suppose a 1-kg parcel of dry air is rising at a constant vertical velocity.
If the parcel is being heated by radiation at the rate of {heating_rate} W kg^-1,
what must the speed of rise be to maintain the parcel at a constant temperature?
        """
        self.func = self.calculate_vertical_velocity
        self.default_variables = {
            "heating_rate": 0.1  # Heating rate by radiation (W/kg)
        }
        self.constant = {
            "gravity": 9.8       # Gravitational acceleration (m/s^2)
        }
        self.independent_variables = {
            "heating_rate": {"min": 0.01, "max": 1.0, "granularity": 0.01}
        }
        self.dependent_variables = {}
        self.choice_variables = {}
        self.custom_constraints = [
            lambda vars, res: vars["heating_rate"] > 0 and res > 0
        ]
        super(Question46, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_vertical_velocity(heating_rate, gravity):
        """
        Calculate the vertical velocity required to maintain a constant temperature
        for a rising parcel of dry air.

        Parameters:
        heating_rate (float): Heating rate by radiation (W/kg).
        gravity (float): Gravitational acceleration (m/s^2).

        Returns:
        float: Vertical velocity (m/s) required to maintain a constant temperature.
        """
        return Answer(heating_rate / gravity, "m/s", 4)


if __name__ == '__main__':
    q = Question46(unique_id="q")
    print(q.question())
    print(q.answer())