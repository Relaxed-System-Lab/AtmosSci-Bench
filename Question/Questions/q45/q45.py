import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question45(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Geophysics"
        self.template = """
Derive an expression for the altitude variation of the pressure change δp that occurs when an atmosphere with constant lapse rate is subjected to a height independent temperature change δT while surface pressure remains constant. At what height is the magnitude of the pressure change a maximum if the lapse rate is {gamma} K/km, T0={T0}, and δT={delta_T} K?
        """
        self.func = self.calculate_pressure_variation
        self.default_variables = {
            "T0": 300,  # Surface temperature (K)
            "delta_T": 2,  # Temperature change (K)
            "gamma": 6.5,  # Lapse rate (K/km)
        #   "Z": 8.0,  # Height for evaluation (km)
        }

        self.constant = {
            "g0": 9.81,  # Gravitational acceleration (m/s^2)
            "R": 287,  # Gas constant for air (J/(kg*K))
        }

        self.independent_variables = {
            "T0": {"min": 200, "max": 350, "granularity": 1},
            "delta_T": {"min": 0.5, "max": 5, "granularity": 0.1},
            "gamma": {"min": 4.0, "max": 10.0, "granularity": 0.1},
        }

        self.dependent_variables = {
        #   "Z": lambda vars: vars["T0"] / vars["gamma"] * 0.1,
        }

        self.choice_variables = {
        }

        self.custom_constraints = [
            lambda vars, res: vars["T0"] > vars["delta_T"],  # Surface temp must be higher than the change
        ]

        super(Question45, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_pressure_variation(T0, delta_T, gamma, g0, R):
        """
        Calculate the altitude variation of the pressure change and the height at which it is maximized.

        Parameters:
            T0 (float): Surface temperature (K).
            delta_T (float): Temperature change (K).
            gamma (float): Lapse rate (K/km).
            g0 (float): Gravitational acceleration (m/s^2).
            R (float): Gas constant for air (J/(kg*K)).
            Z (float): Height for evaluation (km).

        Returns:
            tuple: (delta_p_over_p0, Z_max)
                - delta_p_over_p0: Pressure change ratio at given Z.
                - Z_max: Height at which pressure change is maximum (km).
        """
        # Calculate epsilon
        epsilon = (g0 / (R * gamma)) - 1

        # Pressure change ratio delta_p / p0
        # term1 = (1 - (gamma * Z) / (T0 + delta_T)) ** (g0 / (R * gamma))
        # term2 = (1 - (gamma * Z) / T0) ** (g0 / (R * gamma))
        # delta_p_over_p0 = term1 - term2

        # Height Z_max where delta_p is maximized
        T_ratio = T0 / (T0 + delta_T)
        Z_max = (T0 / gamma) * (1 - T_ratio ** (1 / epsilon)) / (1 - T_ratio ** (1 + 1 / epsilon))

        Z_max_in_km = Z_max / 1000
        return Answer(Z_max_in_km, "km", 3)



if __name__ == '__main__':
    q = Question45(unique_id="q")
    print(q.question())
    print(q.answer())