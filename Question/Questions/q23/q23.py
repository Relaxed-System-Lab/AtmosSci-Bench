import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question23(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """ An air parcel at {p} hPa with temperature {T} K is saturated (mixing ratio {qs} kg/kg). Compute {{θ_e}} for the parcel.
        """
        self.func = self.calculate_theta_e
        self.default_variables = {
            "T": 293.15,  # Temperature in Kelvin
            "p": 920,     # Parcel pressure in hPa
            # "ps": 1000,   # Reference pressure in hPa
            "qs": 16e-3   # Mixing ratio in kg/kg
        }
        self.constant = {
            "ps": 1000,   # Reference pressure in hPa
        }

        self.independent_variables = {
            "T": {"min": 250.0, "max": 310.0, "granularity": 0.1},
            "p": {"min": 800.0, "max": 1050.0, "granularity": 1.0},
        #   "ps": {"min": 900.0, "max": 1050.0, "granularity": 1.0},  ps is a fixed reference value
            "qs": {"min": 0.001, "max": 0.02, "granularity": 1e-4},
        }
        self.dependent_variables = {}
        self.choice_variables = {}
        self.custom_constraints = [
        #   lambda vars, res: vars["p"] < vars["ps"],
            lambda vars, res: vars["T"] > 0
        ]

        super(Question23, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_theta_e(T, p, ps, qs, Lc=2.5e6, cp=1004, R=287):
        """
        Calculate the equivalent potential temperature (theta_e) of an air parcel.

        Parameters:
            T (float): Temperature in Kelvin (e.g., 293.15 K for 20°C).
            p (float): Pressure of the air parcel in hPa (e.g., 920 hPa).
            ps (float): Reference pressure (e.g., 1000 hPa).
            qs (float): Mixing ratio in kg/kg (e.g., 16 g/kg = 16e-3 kg/kg).
            Lc (float): Latent heat of condensation in J/kg (default is 2.5e6 J/kg).
            cp (float): Specific heat capacity at constant pressure in J/(kg·K) (default is 1004 J/(kg·K)).
            R (float): Specific gas constant for dry air in J/(kg·K) (default is 287 J/(kg·K)).

        Returns:
            float: Equivalent potential temperature (theta_e) in Kelvin.
        """
        # Calculate potential temperature (theta)
        theta = T * (ps / p) ** (R / cp)

        # Calculate the exponent term for theta_e
        exponent = (Lc * qs) / (cp * T)

        # Calculate theta_e
        theta_e = theta * math.exp(exponent)

        return Answer(theta_e, "K", 0)



if __name__ == '__main__':
    q = Question23(unique_id="q")
    print(q.question())
    print(q.answer())