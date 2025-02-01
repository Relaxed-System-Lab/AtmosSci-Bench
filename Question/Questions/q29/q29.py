import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer

class Question29(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """
Use the hydrostatic equation to show that the mass of a vertical column of air of unit cross-section, extending from the ground to great height, is $\frac{{p_{{s}}}}{{g}}$, where ${{p_{{s}}}} is the surface pressure. Insert numbers to estimate the mass on a column of air of area {column_area} m^2. Use your answer to estimate the total mass of the atmosphere.
        """

        self.func = self.calculate_mass

        self.default_variables = {
            "column_area": 1         # m^2
        }

        self.constant = {
            "gravity": 9.81,         # m/s^2
            "earth_radius": 6.37e6,   # meters
            "surface_pressure": 1e5,  # Pascals
        }

        self.independent_variables = {
        #   "surface_pressure": {"min": 5e4, "max": 2e5, "granularity": 1e3},
            "column_area": {"min": 0.1, "max": 10.0, "granularity": 0.1},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = []

        super(Question29, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_mass(surface_pressure, gravity, earth_radius, column_area):
        """
        Calculate the mass of a column of air and the total mass of the atmosphere.

        Parameters:
            surface_pressure (float): Surface pressure in Pascals (Pa).
            gravity (float): Gravitational acceleration in m/s^2.
            earth_radius (float): Earth's radius in meters.
            column_area (float): Area of the column cross-section in m^2.

        Returns:
            tuple: (mass_of_column, total_mass_of_atmosphere)
                mass_of_column (float): Mass of the air column in kilograms.
                total_mass_of_atmosphere (float): Total mass of the atmosphere in kilograms.
        """
        # Calculate mass of a column of air of given cross-sectional area
        mass_of_column = (surface_pressure / gravity) * column_area

        # Calculate total mass of the atmosphere
        total_mass_of_atmosphere = (4 * math.pi * earth_radius**2 * surface_pressure) / gravity

        return NestedAnswer({
            "mass_of_column": Answer(mass_of_column, "kg", 0),
            "total_mass_of_atmosphere": Answer(total_mass_of_atmosphere, "kg", 0)
        })



if __name__ == '__main__':
    q = Question29(unique_id="q")
    print(q.question())
    print(q.answer())