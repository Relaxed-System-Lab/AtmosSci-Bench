import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question88(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Physical Oceanography"
        self.template = """Determine the Ekman number for the {region_name}, using typical values, U={U} m s^-1, L={L} km, and an approximate eddy viscosity A={A} m^2 s^-1."""
        self.func = self.calculate_ekman_number

        self.default_variables = {
            "U": 1.0,       # Characteristic velocity (m/s), not used directly in Ekman calculation but included for context
            "L": 100.0,     # Characteristic length scale in kilometers
            "A": 1e5,       # Eddy viscosity in m^2/s
            "f": 9.2e-5,     # Coriolis parameter in 1/s
            "region_name": "Gulf Stream"  # Default region name
        }

        self.constant = {
            # "pi": 3.14159  # Example constant (not used here but placeholder if needed)
        }

        self.independent_variables = {
            "L": {"min": 50.0, "max": 500.0, "granularity": 1.0},   # in km, not too small
            "A": {"min": 1e3, "max": 5e5, "granularity": 1e3},       # in m^2/s, not too large
            # "f": {"min": 5e-5, "max": 2e-4, "granularity": 1e-5},    # in 1/s, avoid equator-like values
        }

        self.dependent_variables = {
            "U": lambda vars: 1.0  # Velocity is a placeholder context variable, not needed for Ekman number
        }

        self.choice_variables = {
            "region": [
                {"region_name": "Equator", "f": 1.0e-6},                    # 0°N
                {"region_name": "Amazon Basin", "f": 2.5e-5},               # ~3°S
                {"region_name": "Bay of Bengal", "f": 4.5e-5},              # ~10°N
                {"region_name": "Arabian Sea", "f": 6.3e-5},                # ~15°N
                {"region_name": "Gulf of Mexico", "f": 7.5e-5},             # ~20°N
                {"region_name": "Florida Current", "f": 8.7e-5},            # ~25°N
                {"region_name": "Gulf Stream", "f": 9.2e-5},                # ~30°N
                {"region_name": "Canary Current", "f": 1.03e-4},            # ~35°N
                {"region_name": "California Current", "f": 1.07e-4},        # ~37°N
                {"region_name": "North Atlantic Drift", "f": 1.11e-4},      # ~40°N
                {"region_name": "Sea of Japan", "f": 1.2e-4},               # ~45°N
                {"region_name": "Labrador Sea", "f": 1.3e-4},               # ~50°N
                {"region_name": "Norwegian Sea", "f": 1.4e-4},              # ~60°N
                {"region_name": "Barents Sea", "f": 1.45e-4},               # ~65°N
                {"region_name": "Arctic Ocean", "f": 1.46e-4},              # ~70°N
                {"region_name": "Southern Ocean", "f": 1.2e-4},             # ~60°S
                {"region_name": "Tasman Sea", "f": 1.0e-4},                 # ~40°S
                {"region_name": "South Pacific Gyre", "f": 7.5e-5},         # ~30°S
                {"region_name": "Agulhas Current", "f": 6.0e-5},            # ~25°S
                {"region_name": "Benguela Current", "f": 5.0e-5},           # ~20°S
                {"region_name": "Peru Current", "f": 3.5e-5},               # ~10°S
                {"region_name": "South Equatorial Current", "f": 2.0e-5},   # ~5°S
                {"region_name": "Indonesian Throughflow", "f": 1.5e-5},     # ~5°N
                {"region_name": "Red Sea", "f": 6.5e-5},                    # ~20°N
                {"region_name": "South China Sea", "f": 7.0e-5},            # ~15°N
            ]
        }


        self.custom_constraints = [
            lambda vars, res: res < 10  # Ekman number should typically be << 10 to indicate Coriolis dominance
        ]

        super(Question88, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_ekman_number(U, L, A, f, region_name):
        """
        Calculate the Ekman number.

        Parameters:
        - U: Characteristic velocity (m/s), included for context (not used)
        - L: Characteristic length scale (km, converted to m inside)
        - A: Eddy viscosity (m^2/s)
        - f: Coriolis parameter (1/s)

        Returns:
        - Ekman number (float)
        """
        L_meters = L * 1e3  # Convert km to meters
        Ek = A / (f * L_meters ** 2)
        return Answer(Ek, "", 4)


if __name__ == '__main__':
    q = Question88(unique_id="q")
    print(q.question())
    print(q.answer())