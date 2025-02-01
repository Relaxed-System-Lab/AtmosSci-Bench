import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer

class Question22(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """Compute the rate of change of circulation about a square in the (x, y) plane with corners at (0,0),(0, L),(L, L), and (L, 0) if temperature increases eastward at a rate of {temp_gradient} °C per {temp_distance} km and pressure increases northward at a rate of {pressure_gradient} hPa per {pressure_distance} km. Let L={side_length} km and the pressure at the point (0,0) be {initial_pressure} hPa."""
        self.func = self.compute_rate_of_change_circulation
        self.default_variables = {
            "temp_gradient": 1,  # Temperature increase (°C)
            "pressure_gradient": 1,  # Pressure increase (hPa)
            "side_length": 1000,  # Side length of the square (km)
            "temp_distance": 200,  # Distance for temperature gradient (km)
            "pressure_distance": 200  # Distance for pressure gradient (km)
        }
        self.constant = {
            "initial_pressure": 1000,  # Initial pressure at (0, 0) (hPa)
        }

        self.independent_variables = {
            "temp_gradient": {"min": 0.5, "max": 5, "granularity": 0.5},
            "pressure_gradient": {"min": 0.5, "max": 5, "granularity": 0.5},
            "side_length": {"min": 100, "max": 2000, "granularity": 100},
            "temp_distance": {"min": 100, "max": 500, "granularity": 100},
            "pressure_distance": {"min": 100, "max": 500, "granularity": 100}
        }
        self.dependent_variables = {}
        self.choice_variables = {}
        self.custom_constraints = []

        super(Question22, self).__init__(unique_id, seed, variables)

    @staticmethod
    def compute_rate_of_change_circulation(
        temp_gradient,  # Temperature increase rate (°C per km)
        pressure_gradient,  # Pressure increase rate (hPa per km)
        side_length,  # Side length of the square (km)
        initial_pressure,  # Initial pressure at (0, 0) (hPa)
        temp_distance,  # Distance for temperature gradient (km)
        pressure_distance  # Distance for pressure gradient (km)
    ):
        """
        Computes the rate of change of circulation about a square in the (x, y) plane.

        Parameters:
            temp_gradient (float): Temperature increase rate (°C per km).
            pressure_gradient (float): Pressure increase rate (hPa per km).
            side_length (float): Side length of the square (km).
            initial_pressure (float): Initial pressure at (0, 0) (hPa).
            temp_distance (float): Distance for temperature gradient (km).
            pressure_distance (float): Distance for pressure gradient (km).

        Returns:
            float: Rate of change of circulation (m^2/s^2).
        """
        import math

        # Convert gradients to total differences over the side length
        delta_temp = temp_gradient * (side_length / temp_distance)  # °C
        delta_pressure = pressure_gradient * (side_length / temp_distance)  # hPa

        # Convert hPa to Pa for natural logarithm calculation
        # p0 = initial_pressure * 100  # Pa
        # p1 = (initial_pressure + delta_pressure) * 100  # Pa

        p0 = initial_pressure
        p1 = initial_pressure + delta_pressure

        # Compute the natural logarithm of the pressure ratio
        ln_pressure_ratio = math.log(p1 / p0)

        # print("delta_temp: ", delta_temp)
        # print("ln_pressure_ratio: ", ln_pressure_ratio)

        # Compute the rate of change of circulation
        rate_of_change = -287 * delta_temp * ln_pressure_ratio

        return Answer(rate_of_change, "m^2/s^2", 1)



if __name__ == '__main__':
    q = Question22(unique_id="q")
    print(q.question())
    print(q.answer())