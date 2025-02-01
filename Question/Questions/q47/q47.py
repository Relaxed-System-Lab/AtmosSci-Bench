import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question47(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """ An air parcel that has a temperature of {t_initial}\u00b0C at the {p_initial} hPa level is lifted dry adiabatically. What is its density when it reaches the {p_final} hPa level? """
        self.func = self.calculate_density

        self.default_variables = {
            "p_initial": 1000,  # Initial pressure (hPa)
            "t_initial": 20,    # Initial temperature (\u00b0C)
            "p_final": 500,     # Final pressure (hPa)
        }

        self.constant = {
            "R": 287,          # Specific gas constant for dry air (J/(kg*K))
            "c_p": 1004,       # Specific heat at constant pressure (J/(kg*K))
            "c_v": 717         # Specific heat at constant volume (J/(kg*K))
        }

        self.independent_variables = {
            "p_initial": {"min": 500, "max": 1100, "granularity": 1},
            "t_initial": {"min": -50, "max": 50, "granularity": 0.1},
        }

        self.dependent_variables = {
            "p_final": lambda vars: vars["p_initial"] * 0.5,
        }

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["p_initial"] > vars["p_final"]
        ]
        super(Question47, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_density(p_initial, t_initial, p_final, R=287, c_p=1004, c_v=717):
        """
        Calculate the density of an air parcel lifted dry adiabatically.

        Parameters:
            p_initial (float): Initial pressure (hPa)
            t_initial (float): Initial temperature (\u00b0C)
            p_final (float): Final pressure (hPa)
            R (float): Specific gas constant for dry air (J/(kg*K)).
            c_p (float): Specific heat at constant pressure (J/(kg*K)).
            c_v (float): Specific heat at constant volume (J/(kg*K)).

        Returns:
            float: Density of the air parcel at the final pressure (kg/m^3).
        """
        # Convert units
        p_initial_pa = p_initial * 100  # Convert hPa to Pa
        p_final_pa = p_final * 100      # Convert hPa to Pa
        t_initial_k = t_initial + 273.15  # Convert \u00b0C to K

        # Calculate the exponent (cv/cp)
        gamma = c_v / c_p

        # Calculate initial density
        rho_initial = p_initial_pa / (R * t_initial_k)

        # Calculate final density
        rho_final = rho_initial * (p_final_pa / p_initial_pa) ** gamma

        return Answer(rho_final, "kg/m^3", 3)


if __name__ == '__main__':
    q = Question47(unique_id="q")
    print(q.question())
    print(q.answer())