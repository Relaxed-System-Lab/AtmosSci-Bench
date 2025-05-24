import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question100(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """Utilize Equation 1 to calculate the depth and average velocity of a flow in a channel characterized by a slope S={S}, width w={w} m, discharge Q={Q} m³/s, and Manning's n={n}. Is it reasonable to assume that RH ≈ h for this flow? 
$$
\begin{{equation*}}
q_{{w}}=U h=\frac{{k}}{{n}} h^{{5 / 3}} S^{{1 / 2}} . \tag{{Equation 1}}
\end{{equation*}}
$$"""

        self.func = self.calculate_channel_flow
        self.default_variables = {
            "Q": 1.0,     # Discharge in m³/s
            "w": 15.0,    # Channel width in m
            "S": 0.003,   # Slope (dimensionless)
            "n": 0.075    # Manning's roughness coefficient
        }

        self.constant = {
            "k": 1.0  # SI unit coefficient in Manning's equation
        }

        self.independent_variables = {
            "Q": {"min": 0.1, "max": 20.0, "granularity": 0.1},
            "w": {"min": 1.0, "max": 30.0, "granularity": 0.5},
            "S": {"min": 0.0001, "max": 0.01, "granularity": 0.0001},
            "n": {"min": 0.01, "max": 0.15, "granularity": 0.005}
        }

        self.dependent_variables = {
            # RH is derived and not explicitly sampled
        }

        self.choice_variables = {
        }

        self.custom_constraints = [
            lambda vars, res: res["RH_close_to_h"] == True  # RH ≈ h must be within 5% margin
        ]

        super(Question100, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_channel_flow(Q, w, S, n, k=1.0):
        """
        Estimates the depth (h), mean velocity (U), and checks if RH ≈ h is reasonable.
        
        Parameters:
        - Q: Discharge (m³/s)
        - w: Channel width (m)
        - S: Slope (unitless)
        - n: Manning's roughness coefficient
        - k: Manning's unit coefficient (default 1.0 for SI)
        
        Returns:
        - h: Estimated flow depth (m)
        - U: Mean velocity (m/s)
        - RH_close_to_h: Whether RH ≈ h (within 5%)
        """
        qw = Q / w  # specific discharge in m²/s

        h = ((qw * n) / (k * math.sqrt(S))) ** (3 / 5)

        U = qw / h

        A = w * h
        P = w + 2 * h
        RH = A / P

        RH_close_to_h = abs(RH - h) / h <= 0.05

        return NestedAnswer({
            "depth": Answer(h, "m", 2),
            "mean_velocity": Answer(U, "m/s", 2),
            "RH_close_to_h": Answer(RH_close_to_h, "", None)
        })

if __name__ == '__main__':
    q = Question100(unique_id="q")
    print(q.question())
    print(q.answer())