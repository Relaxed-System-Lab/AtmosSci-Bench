import random, math
from ..question import Question
from Questions.answer import Answer


class Question4(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
#         self.template = """
# Calculate the solar constant at the orbit of {planet_name} based on what you have learned from the Sun - Earth Geometry, given the following values:

# | Temperature of the Sun (T_s) | T_s = {T_s} K |
# | :--- | :---: |
# | Radius of the Sun (R_s) | R_s = {R_s} km |
# | Distance of Sun's surface to {planet_name} (D_v) | D_v = {D_v} km |
# | The Stefan-Boltzmann constant (σ) | σ = 5.67e-8 W/m^2/K^4 |

# Clearly state the laws or assumptions for the key steps, otherwise marks will be deducted. (Celsius $=$ Kelvin -273 )
# ![](https://cdn.mathpix.com/cropped/2024_12_06_b79d610f0ffcf56a3450g-01.jpg?height=356&width=929&top_left_y=1087&top_left_x=569)
#         """
        self.template = """
Calculate the solar constant at the orbit of {planet_name} based on what you have learned from the Sun - Earth Geometry, given the following values:

| Temperature of the Sun (T_s) | T_s = {T_s} K |
| :--- | :---: |
| Radius of the Sun (R_s) | R_s = {R_s} km |
| Distance of Sun's surface to {planet_name} (D_v) | D_v = {D_v} km |
| The Stefan-Boltzmann constant (σ) | σ = 5.67e-8 W/m^2/K^4 |

Clearly state the laws or assumptions for the key steps, otherwise marks will be deducted. (Celsius $=$ Kelvin -273 )
        """
        self.func = self.calculate_solar_constant
        self.default_variables = {
            "planet_name": "Venus",
            "T_s": 5800,  # Temperature of the Sun (K)
            "R_s": 7e5,   # Radius of the Sun (km)
            "D_v": 1e8,   # Distance to Venus (km)
            # "R_v": 6052,  # Radius of Venus (km)
            # "sigma": 5.67e-8  # Stefan-Boltzmann constant (W/m^2/K^4)
        }

        self.independent_variables = {
            "T_s": {"min": 1000, "max": 10000, "granularity": 10},       # Kelvin
            "R_s": {"min": 1e4, "max": 2e6, "granularity": 1000},        # kilometers
        }
        self.dependent_variables = {}

        self.choice_variables = {
            "c1": [
                {"planet_name": "Mercury", "D_v": 5.79e7},  # Distance in kilometers
                {"planet_name": "Venus", "D_v": 1.08e8},   # Distance in kilometers
                {"planet_name": "Earth", "D_v": 1.496e8},  # Distance in kilometers
                {"planet_name": "Mars", "D_v": 2.279e8},   # Distance in kilometers
                {"planet_name": "Jupiter", "D_v": 7.785e8},# Distance in kilometers
                {"planet_name": "Saturn", "D_v": 1.433e9}, # Distance in kilometers
                {"planet_name": "Uranus", "D_v": 2.877e9}, # Distance in kilometers
                {"planet_name": "Neptune", "D_v": 4.503e9} # Distance in kilometers
            ]
        }

        self.custom_constraints = [
        ]

        super(Question4, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_solar_constant(planet_name, T_s, R_s, D_v):
        """
        Calculate the solar constant at Venus's orbit.

        Parameters:
        T_s (float): Temperature of the Sun (K)
        R_s (float): Radius of the Sun (km)
        D_v (float): Distance from Sun to Venus (km)
        R_v (float): Radius of Venus (km) [Not directly used]
        sigma (float): Stefan-Boltzmann constant (W/m^2/K^4)

        Returns:
        float: Solar constant at Venus's orbit (W/m^2)
        """
        sigma = 5.67e-8
        R_v = None  # Not used in the calculation

        # Convert radius and distance to meters
        R_s_m = R_s * 1e3  # Sun's radius in meters
        D_v_m = D_v * 1e3  # Distance to Venus in meters

        # Total radiant power of the Sun using Stefan-Boltzmann law
        E_s = 4 * math.pi * R_s_m**2 * sigma * T_s**4

        # Solar constant at Venus
        S_v = E_s / (4 * math.pi * D_v_m**2)

        return Answer(S_v, "W/m^2", 2)

if __name__ == '__main__':
    q = Question4(unique_id="q")
    print(q.question())
    print(q.answer())