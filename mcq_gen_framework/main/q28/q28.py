import random, math
from question import Question
from answer import Answer, NestedAnswer


class Question28(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Geophysics"
        self.template = """Calculate the emission temperature for the planet {planet_name}. Assume that: the average orbital radius of {planet_name} is {orbital_radius_ratio} times that of Earth's orbit. Considering the solar flux diminishes with the square of the distance from the sun and that the planetary albedo of {planet_name} is {albedo}, find the emission temperature of {planet_name}."""

        self.func = self.calculate_emission_temperature

        self.default_variables = {
            "planet_name": "Venus",
            "orbital_radius_ratio": 0.72,  # Ratio of orbital radius of Venus to Earth
            "albedo": 0.77  # Planetary albedo
        }

        self.constant = {
            "stefan_boltzmann_constant": 5.67e-8  # Stefan-Boltzmann constant (W/m^2/K^4)
        }

        self.independent_variables = {
            "orbital_radius_ratio": {"min": 0.1, "max": 2.0, "granularity": 0.01},
            "albedo": {"min": 0.0, "max": 1.0, "granularity": 0.01}
        }

        self.dependent_variables = {}

        self.choice_variables = {
            "planet": [
                {"planet_name": "Mercury", "orbital_radius_ratio": 0.39, "albedo": 0.12},
                {"planet_name": "Venus", "orbital_radius_ratio": 0.72, "albedo": 0.77},
                {"planet_name": "Mars", "orbital_radius_ratio": 1.52, "albedo": 0.25},
            ]
        }

        self.custom_constraints = []

        super(Question28, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_emission_temperature(orbital_radius_ratio, albedo, stefan_boltzmann_constant, planet_name):
        """
        Calculate the emission temperature of a planet.

        Parameters:
        orbital_radius_ratio (float): Ratio of the planet's orbital radius to Earth's orbital radius
        albedo (float): Planetary albedo (reflectivity)
        stefan_boltzmann_constant (float): Stefan-Boltzmann constant (W/m^2/K^4)

        Returns:
        float: Emission temperature of the planet (K)
        """
        solar_flux_earth = 1367 # Solar flux at Earth's orbit (W/m^2)

        # Calculate solar flux at the planet
        solar_flux_planet = solar_flux_earth / (orbital_radius_ratio ** 2)

        # Calculate emission temperature using the given formula
        temperature = (
            (solar_flux_planet * (1 - albedo)) / (4 * stefan_boltzmann_constant)
        ) ** 0.25

        return Answer(temperature, "K", 1)

if __name__ == '__main__':
    q = Question28(unique_id="q")
    print(q.question())
    print(q.answer())