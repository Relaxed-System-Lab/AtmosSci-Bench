import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer
import numpy as np


class Question59(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
The divergence of the horizontal wind at various pressure levels above a given station is shown in the following table.

| Pressure ${{\\mathbf{{hPa}}}}$ | ${{\\boldsymbol{{\\nabla}} \\cdot \\mathbf{{V}} \\mathbf{{( \\times \\mathbf {{ 10 }} ^ {{ - \\mathbf {{ 5 }} }} \\mathbf {{ s }} ^ {{ \\mathbf {{ - 1 }} }} )}}}}$ |
| :---: | :---: |
| {p1} | {div1} |
| {p2} | {div2} |
| {p3} | {div3} |
| {p4} | {div4} |
| {p5} | {div5} |
| {p6} | {div6} |

Compute the vertical velocity at each level assuming an isothermal atmosphere with temperature {temp} K and letting $w=0$ at {p1} hPa
"""
        self.func = self.calculate_vertical_velocities

        self.default_variables = {
            "p1": 1000,
            "p2": 850,
            "p3": 700,
            "p4": 500,
            "p5": 300,
            "p6": 100,
            "div1": 0.9,
            "div2": 0.6,
            "div3": 0.3,
            "div4": 0.0,
            "div5": -0.6,
            "div6": -1.0,
            "temp": 260
        }

        self.constant = {
            "gravity": 9.81,
            "gas_constant": 287.0
        }

        self.independent_variables = {
            "p1": {"min": 900, "max": 1100, "granularity": 50, "fixed_precision": True},  # hPa
            "div1": {"min": -2.0, "max": 2.0, "granularity": 0.1},  # divergence
            "temp": {"min": 230, "max": 300, "granularity": 5},  # temperature in K
        }

        self.dependent_variables = {
            # Random reduction between 50 and p1/5 hPa
            "p2": lambda vars: vars["p1"] - np.random.randint(50, vars["p1"] // 5),
            "p3": lambda vars: vars["p2"] - np.random.randint(50, vars["p1"] // 5),
            "p4": lambda vars: vars["p3"] - np.random.randint(50, vars["p1"] // 5),
            "p5": lambda vars: vars["p4"] - np.random.randint(50, vars["p1"] // 5),
            "p6": lambda vars: vars["p5"] - np.random.randint(50, vars["p1"] // 5),
            # Divergence decreases randomly between 0.1-0.6
            "div2": lambda vars: round(vars["div1"] - np.random.randint(1, 6) * 0.1, 1),
            "div3": lambda vars: round(vars["div2"] - np.random.randint(1, 6) * 0.1, 1),
            "div4": lambda vars: round(vars["div3"] - np.random.randint(1, 6) * 0.1, 1),
            "div5": lambda vars: round(vars["div4"] - np.random.randint(1, 6) * 0.1, 1),
            "div6": lambda vars: round(vars["div5"] - np.random.randint(1, 6) * 0.1, 1),
        }

        self.choice_variables = {}

        self.custom_constraints = [
                lambda vars, res: all([vars["p1"] > 0, vars["p2"] >  0, vars["p3"] >  0, vars["p4"] > 0, vars["p5"] >  0, vars["p6"] >  0]),  # Ensure pressures are not 0
            # lambda vars, res: vars["p1"] > vars["p6"],  # Ensure pressures decrease
            # lambda vars, res: vars["div1"] >= vars["div6"],  # Ensure divergence decreases
            # lambda vars, res: all(vars[f"p{i}"] > 0 for i in range(2, 7)),  # All pressures > 0
        ]

        super(Question59, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_vertical_velocities(p1, p2, p3, p4, p5, p6, div1, div2, div3, div4, div5, div6, temp, gravity=9.81, gas_constant=287.0):
        """
        Calculate vertical pressure velocity (omega) and vertical velocity (w) at each pressure level.
        """
        import numpy as np

        pressure_levels = [p1, p2, p3, p4, p5, p6]
        divergence = [div1, div2, div3, div4, div5, div6]

        pressure_levels_pa = np.array(pressure_levels) * 100  # Convert to Pa
        divergence_values = np.array(divergence) * 1e-5  # Convert to s^-1
        
        omega = np.zeros(len(pressure_levels_pa))
        w = np.zeros(len(pressure_levels_pa))

        for i in range(1, len(pressure_levels_pa)):
            p0, p1 = pressure_levels_pa[i-1], pressure_levels_pa[i]
            div_avg = 0.5 * (divergence_values[i-1] + divergence_values[i])
            omega[i] = omega[i-1] + (p0 - p1) * div_avg

        factor = -(gas_constant * temp / gravity) * 1e2  # cm/s
        for i in range(1, len(pressure_levels_pa)):
            w[i] = factor * (omega[i] / pressure_levels_pa[i])

        # return omega.tolist(), w.tolist()
        answer_lst = [Answer(x, "cm/s", 2) for x in w.tolist()]
        return NestedAnswer({
            p2: answer_lst[1],
            p3: answer_lst[2],
            p4: answer_lst[3],
            p5: answer_lst[4],
            p6: answer_lst[5]
        })


if __name__ == '__main__':
    q = Question59(unique_id="q")
    print(q.question())
    print(q.answer())