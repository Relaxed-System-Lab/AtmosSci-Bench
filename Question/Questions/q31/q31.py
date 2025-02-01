import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question31(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """
Consider a horizontally uniform atmosphere in hydrostatic balance. The atmosphere is isothermal, with temperature of {temperature} K. Surface pressure is {surface_pressure} Pa.

(a) Consider the level that divides the atmosphere into two equal parts by mass (i.e., one-half of the atmospheric mass is above this level). What is the altitude, pressure, density, and potential temperature at this level?

(b) Repeat the calculation of part (a) for the level below which lies {percentage_mass_below}% of the atmospheric mass.
        """
        self.func = self.calculate_isothermal_atmosphere_properties
        self.default_variables = {
            "temperature": 263,         # Temperature in K
            "percentage_mass_below": 90 # Percentage of mass below
        }

        self.constant = {
            "surface_pressure": 100000,  # Surface pressure in Pa
            "gas_constant": 287,       # Specific gas constant, J/(kg·K)
            "gravity": 9.8             # Acceleration due to gravity, m/s²
        }

        self.independent_variables = {
            "temperature": {"min": 250, "max": 310, "granularity": 1},
            "percentage_mass_below": { "min": 10, "max":90, "granularity": 1}
        }

        self.dependent_variables = {
        }

        self.choice_variables = {
        }

        self.custom_constraints = [
        ]

        super(Question31, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_isothermal_atmosphere_properties(surface_pressure, temperature, percentage_mass_below, gas_constant=287, gravity=9.8):
        """
        Calculate properties of an isothermal atmosphere in hydrostatic balance.

        Parameters:
            surface_pressure (float): Surface pressure in Pa.
            temperature (float): Temperature in Kelvin.
            percentage_mass_below (float): Percentage of mass below the level.
            gas_constant (float): Specific gas constant, default is 287 J/(kg·K).
            gravity (float): Acceleration due to gravity, default is 9.8 m/s².

        Returns:
            dict: A dictionary with the calculated altitude, pressure, and density for both parts (a) and (b).
        """
        # Calculate scale height
        scale_height = gas_constant * temperature / gravity  # in meters

        def calculate_properties(fraction_mass_above):
            pressure = surface_pressure * fraction_mass_above
            altitude = -scale_height * math.log(pressure / surface_pressure) / 1000  # convert to km
            density = pressure / (gas_constant * temperature)
            return altitude, pressure, density

        # Part (a): Half mass above
        altitude_a, pressure_a, density_a = calculate_properties(0.5)

        # Part (b): Mass below as given
        fraction_mass_above_b = 1 - percentage_mass_below / 100
        altitude_b, pressure_b, density_b = calculate_properties(fraction_mass_above_b)

        return NestedAnswer({
            "(a)": NestedAnswer({"altitude": Answer(altitude_a, "km", 2), "pressure": Answer(pressure_a, "Pa", 0), "density": Answer(density_a, "kg/m^3", 3)}),
            "(b)": NestedAnswer({"altitude": Answer(altitude_b, "km", 2), "pressure": Answer(pressure_b, "Pa", 0), "density": Answer(density_b, "kg/m^3", 3)})
        })



if __name__ == '__main__':
    q = Question31(unique_id="q")
    print(q.question())
    print(q.answer())