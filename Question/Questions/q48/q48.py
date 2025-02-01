import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question48(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
Suppose an air parcel starts from rest at the {p1} hPa level and rises vertically to {p2} hPa while maintaining a constant {T_excess}°C temperature excess over the environment. Assuming that the mean temperature of the {p1}-{p2} hPa layer is {mean_T} K, compute the energy released owing to the work of the buoyancy force. Assuming that all the released energy is realized as kinetic energy of the parcel, what will the vertical velocity of the parcel be at {p2} hPa?
        """
        self.func = self.calculate_energy_and_velocity

        self.default_variables = {
            "p1": 800,           # Initial pressure (hPa)
            "p2": 500,           # Final pressure (hPa)
            "T0": 261,           # Parcel temperature (K)
            "T_env": 260,        # Environmental temperature (K)
            "mean_T": 260,       # Mean temperature of the layer (K)
            "T_excess": 1        # Temperature excess (°C)
        }
        self.constant = {
            "R": 287.05,         # Specific gas constant for dry air (J/kg·K)
            "g": 9.81            # Acceleration due to gravity (m/s^2)
        }
        self.independent_variables = {
            "p1": {"min": 600, "max": 1000, "granularity": 1},
            "p2": {"min": 300, "max": 700, "granularity": 1},
            "T_env": {"min": 240, "max": 300, "granularity": 1},  #           
            "T_excess": {"min": 0, "max": 5, "granularity": 0.1},
            "mean_T": {"min": 240, "max": 300, "granularity": 1}
        }

        self.dependent_variables = {
            "T0": lambda vars: vars["T_env"] + vars["T_excess"]
        }

        self.choice_variables = {
            # No specific grouped constraints in this question
        }

        self.custom_constraints = [
            lambda vars, res: vars["p1"] > vars["p2"]  # p1 must be greater than p2
        ]

        super(Question48, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_energy_and_velocity(p1, p2, T0, T_env, mean_T, T_excess, R=287.05, g=9.81):
        """
        Calculate the energy released due to the buoyancy force and the vertical velocity of an air parcel.

        Parameters:
        - p1: Initial pressure (hPa)
        - p2: Final pressure (hPa)
        - T0: Temperature of the air parcel (K)
        - T_env: Temperature of the environment (K)
        - mean_T: Mean temperature of the layer (K)

        Returns:
        Tuple containing:
        - Energy released per unit mass (J/kg)
        - Vertical velocity at final pressure level (m/s)
        """
        # Temperature excess
        delta_T = T0 - T_env

        # Compute height difference using the hypsometric equation
        delta_Z = (R * mean_T / g) * math.log(p1 / p2)

        # Energy released per unit mass
        energy_released = g * delta_Z * (delta_T / T0)

        # print("vars", p1, p2, T0, T_env, mean_T, T_excess)
        # print("energy_released", energy_released)

        # Compute vertical velocity assuming all energy goes to kinetic energy
        vertical_velocity = math.sqrt(2 * energy_released)

        return NestedAnswer([Answer(energy_released, "J/kg", 1), Answer(vertical_velocity, "m/s", 2)])


if __name__ == '__main__':
    q = Question48(unique_id="q")
    print(q.question())
    print(q.answer())