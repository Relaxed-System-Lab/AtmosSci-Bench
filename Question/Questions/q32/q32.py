import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question32(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Physics"
        self.template = """
Assume the atmosphere is isothermal with temperature {T_surface} K. 
Determine the potential temperature at altitudes of {alt1} km, {alt2} km, and {alt3} km above the surface. 
If an air parcel were moved adiabatically from {move_from} km to {move_to} km, what would its temperature be on arrival?
        """
        self.func = self.calculate_potential_temperature
        self.default_variables = {
            "T_surface": 280,  # Surface temperature in K
            "alt1": 5,  # Altitude in km
            "alt2": 10,  # Altitude in km
            "alt3": 20,  # Altitude in km
            "move_from": 10,  # Starting altitude in km for adiabatic process
            "move_to": 5  # Destination altitude in km for adiabatic process
        }

        self.constant = {
            "P_surface": 1000,  # Surface pressure in hPa
            "R": 287,  # Specific gas constant for dry air (J/(kg*K))
            "g": 9.81,  # Gravitational acceleration (m/s^2)
            "kappa": 2 / 7  # Ratio of specific heats for air
        }

        self.independent_variables = {
            "T_surface": {"min": 200, "max": 300, "granularity": 1},
            "alt1": {"min": 1, "max": 15, "granularity": 1},
            "alt2": {"min": 10, "max": 20, "granularity": 1},
            "alt3": {"min": 15, "max": 30, "granularity": 1},
        }

        self.dependent_variables = {
            "move_from": lambda vars: vars["alt2"],
            "move_to": lambda vars: vars["alt1"],
        }

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["alt1"] < vars["alt2"] < vars["alt3"],
            lambda vars, res: vars["move_from"] > vars["move_to"]
        ]


        super(Question32, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_potential_temperature(T_surface, alt1, alt2, alt3, move_from, move_to, P_surface=1000, R=287, g=9.81, kappa=2/7):
        """
        Calculate the potential temperature at given altitudes and the temperature of an air parcel after an adiabatic process.

        Parameters:
        T_surface (float): Surface temperature in K
        alt1, alt2, alt3 (float): Altitudes in km for potential temperature calculation
        move_from, move_to (float): Altitudes in km for adiabatic movement calculation
        P_surface (float): Surface pressure in hPa (constant)
        R (float): Specific gas constant for dry air (J/(kg*K)) (constant)
        g (float): Gravitational acceleration (m/s^2) (constant)
        kappa (float): Ratio of specific heats for air (constant)

        Returns:
        dict, float: Potential temperatures at altitudes and temperature on arrival after adiabatic movement.
        """
        # Calculate scale height (H) in km
        H = (R * T_surface) / g / 1000  # Convert m to km

        def pressure_at_altitude(z):
            """Calculate pressure at altitude z (in km)."""
            return P_surface * math.exp(-z / H)

        def potential_temperature(T, P, P_surface):
            """Calculate potential temperature."""
            return T * (P_surface / P) ** kappa

        # Calculate potential temperatures at specified altitudes
        altitudes = [alt1, alt2, alt3]
        results = {}
        for z in altitudes:
            P = pressure_at_altitude(z)
            theta = potential_temperature(T_surface, P, P_surface)
            results[z] = theta

        # Adiabatic process calculation
        P_from = pressure_at_altitude(move_from)
        P_to = pressure_at_altitude(move_to)
        theta_move = results[move_from]  # Potential temperature remains the same
        T_move = theta_move * (P_to / P_surface) ** kappa

        results[f"{move_from}-{move_to}"] = T_move
        # format results
        results = {k: Answer(v, "K", 0) for k, v in results.items()}
        return NestedAnswer(results)


if __name__ == '__main__':
    q = Question32(unique_id="q")
    print(q.question())
    print(q.answer())