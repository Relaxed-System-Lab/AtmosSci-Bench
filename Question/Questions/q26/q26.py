import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question26(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Geophysics"
        self.template = """
Suppose that the {planet_name} is, after all, flat. Specifically, consider it to be a thin circular disk (of radius {radius} km), orbiting the Sun at the same distance as the Earth; the planetary albedo is {albedo}. The vector normal to one face of this disk always points directly toward the Sun, and the disk is made of perfectly conducting material, so both faces of the disk are at the same temperature. Calculate the emission temperature of this disk, and compare with the result we obtained for a spherical Earth.
        """
        self.func = self.calculate_emission_temperature
        self.default_variables = {
            "planet_name": "Earth",  # Name of the planet
            "radius": 6370,  # Radius of the disk (km)
            "albedo": 0.3    # Planetary albedo
        }
        self.independent_variables = {}
        self.dependent_variables = {}
        self.choice_variables = {
            "planet": [
                {"planet_name": "Mercury", "radius": 2440, "albedo": 0.12},
                {"planet_name": "Venus", "radius": 6052, "albedo": 0.75},
                {"planet_name": "Earth", "radius": 6371, "albedo": 0.30},
                {"planet_name": "Mars", "radius": 3390, "albedo": 0.25},
                {"planet_name": "Jupiter", "radius": 69911, "albedo": 0.52},
                {"planet_name": "Saturn", "radius": 58232, "albedo": 0.47},
                {"planet_name": "Uranus", "radius": 25362, "albedo": 0.51},
                {"planet_name": "Neptune", "radius": 24622, "albedo": 0.41},
                {"planet_name": "Pluto", "radius": 1188, "albedo": 0.49},
                {"planet_name": "Alpha Centauri Bb", "radius": 6471, "albedo": 0.35},
                {"planet_name": "Proxima Centauri b", "radius": 7164, "albedo": 0.38},
                {"planet_name": "Kepler-22b", "radius": 12050, "albedo": 0.42},
                {"planet_name": "Gliese 581g", "radius": 7600, "albedo": 0.28},
                {"planet_name": "HD 209458 b", "radius": 15550, "albedo": 0.13},
                {"planet_name": "Kepler-16b", "radius": 8650, "albedo": 0.44},
                {"planet_name": "TRAPPIST-1d", "radius": 5100, "albedo": 0.23},
                {"planet_name": "TRAPPIST-1e", "radius": 5632, "albedo": 0.32},
                {"planet_name": "TRAPPIST-1f", "radius": 5831, "albedo": 0.36},
                {"planet_name": "TRAPPIST-1g", "radius": 5820, "albedo": 0.29},
                {"planet_name": "TRAPPIST-1h", "radius": 3322, "albedo": 0.25},
                {"planet_name": "GJ 1214b", "radius": 16000, "albedo": 0.20},
                {"planet_name": "Kepler-452b", "radius": 11190, "albedo": 0.40},
                {"planet_name": "55 Cancri e", "radius": 8800, "albedo": 0.15},
                {"planet_name": "LHS 1140b", "radius": 7080, "albedo": 0.22},
                {"planet_name": "Kepler-186f", "radius": 6520, "albedo": 0.37},
                {"planet_name": "WASP-12b", "radius": 19050, "albedo": 0.08},
                {"planet_name": "HD 189733b", "radius": 16250, "albedo": 0.31},
                {"planet_name": "Kepler-69c", "radius": 7800, "albedo": 0.34},
                {"planet_name": "Kepler-62f", "radius": 7050, "albedo": 0.30},
                {"planet_name": "Kapteyn b", "radius": 6840, "albedo": 0.28},
                {"planet_name": "GJ 1132b", "radius": 6800, "albedo": 0.21},
                {"planet_name": "Kepler-442b", "radius": 5930, "albedo": 0.38},
                {"planet_name": "TOI 700d", "radius": 6370, "albedo": 0.41},
                {"planet_name": "Kepler-20e", "radius": 3500, "albedo": 0.18},
                {"planet_name": "Kepler-10b", "radius": 4600, "albedo": 0.16},
                {"planet_name": "Kepler-22c", "radius": 9500, "albedo": 0.35},
                {"planet_name": "Kepler-90i", "radius": 7100, "albedo": 0.27},
                {"planet_name": "HD 40307g", "radius": 7700, "albedo": 0.26},
                {"planet_name": "Ross 128 b", "radius": 7100, "albedo": 0.31},
                {"planet_name": "Wolf 1061c", "radius": 6500, "albedo": 0.28},
                {"planet_name": "Gliese 667Cc", "radius": 7150, "albedo": 0.34},
                {"planet_name": "K2-18b", "radius": 8750, "albedo": 0.39},
                {"planet_name": "Kepler-452c", "radius": 11800, "albedo": 0.30},
                {"planet_name": "Tau Ceti f", "radius": 7500, "albedo": 0.25},
                {"planet_name": "Gliese 876d", "radius": 6400, "albedo": 0.29},
                {"planet_name": "Kepler-1649c", "radius": 6200, "albedo": 0.33},
                {"planet_name": "Teegarden b", "radius": 5900, "albedo": 0.31},
                {"planet_name": "Kepler-37b", "radius": 2400, "albedo": 0.20},
                {"planet_name": "HD 69830d", "radius": 7900, "albedo": 0.36}
            ]
        }


        self.custom_constraints = []

        super(Question26, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_emission_temperature(albedo, radius, planet_name):
        """
        Calculate the emission temperature of a flat Earth disk.

        Parameters:
            albedo (float): Planetary albedo (unitless fraction).
            radius (float): Radius of the disk (km).

        Returns:
            float: Emission temperature (K).
        """
        # Define constants
        solar_flux = 1367  # Solar constant (W/m^2)
        stefan_boltzmann = 5.67e-8  # Stefan-Boltzmann constant (W/m^2/K^4)

        # Calculate the emission temperature using the formula
        Te = ((1 - albedo) * solar_flux / (2 * stefan_boltzmann)) ** 0.25
        return Answer(Te, "K", 1)

if __name__ == '__main__':
    q = Question26(unique_id="q")
    print(q.question())
    print(q.answer())