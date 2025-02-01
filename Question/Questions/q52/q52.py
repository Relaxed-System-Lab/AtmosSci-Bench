import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question52(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
Determine the radii of curvature for the trajectories of air parcels located {distance} km to the east, north, south, and west of the center of a circular low-pressure system, respectively. 
The system is moving eastward at {c} m/s. Assume geostrophic flow with a uniform tangential wind speed of {V_g} m/s. 
Then determine the normal gradient wind speeds for the four air parcels using the radii of curvature computed. Compare these speeds with the geostrophic speed. 
(Let f={f} s^-1). Use the gradient wind speeds calculated here to recompute the radii of curvature for the four air parcels. 
Use these new estimates of the radii of curvature to recompute the gradient wind speeds for the four air parcels. 
What fractional error is made in the radii of curvature by using the geostrophic wind approximation in this case?  (Note that further iterations could be carried out, but would rapidly converge.)
        """
        self.func = self.calculate_wind_and_curvature
        self.default_variables = {
            "distance": 500.0,  # Distance from center in km
            "c": 15.0,          # System movement speed in m/s
            "V_g": 15.0,        # Geostrophic wind speed in m/s
        }

        self.constant = {
            "f": 1e-4           # Coriolis parameter in s^-1
        }

        self.independent_variables = {
            "distance": {"min": 100.0, "max": 1000.0, "granularity": 10.0},
            "c": {"min": 5.0, "max": 30.0, "granularity": 1.0},
            "V_g": {"min": 5.0, "max": 30.0, "granularity": 1.0},
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
        #    lambda vars, res: vars["V_g"] > vars["c"]  # Wind speed must exceed system speed
        ]

        super(Question52, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_wind_and_curvature(distance, c, V_g, f, iterations=1):
        """
        Calculate the radii of curvature, gradient wind speeds, and fractional error.

        Parameters:
        - distance (float): Radius of the system in km.
        - c (float): Speed of the system in m/s.
        - V_g (float): Geostrophic wind speed in m/s.
        - f (float): Coriolis parameter in s^-1.
        - iterations (int): Number of iterations for refinement.

        Returns:
        - dict: Results containing initial and final radii, gradient speeds, and fractional errors.
        """
        import math

        km_to_m = 1000  # Conversion factor
        angles = {
            "North": math.pi,
            "South": 0,
            "East": math.pi / 2,
            "West": 3 * math.pi / 2
        }

        results = {
            "R_t_initial": {},
            "V_grad_initial": {},
            "R_t_final": {},
            "V_grad_final": {},
            "Fractional_Error": {}
        }

        # Step 1: Calculate initial radii of curvature
        for direction, gamma in angles.items():
            if V_g == c * math.cos(gamma):
                results["R_t_initial"][direction] = float('inf')
            else:
                R_t = distance / (1 - (c * math.cos(gamma) / V_g))
                results["R_t_initial"][direction] = R_t

        # Step 2: Calculate initial gradient wind speeds
        for direction, R_t in results["R_t_initial"].items():
            if R_t == float('inf'):
                results["V_grad_initial"][direction] = V_g
            else:
                R_t_m = R_t * km_to_m
                term1 = -(f * R_t_m) / 2
                arg = (f * R_t_m / 2) ** 2 + f * R_t_m * V_g
                if arg < 0:
                    arg = 0  # Clamp to avoid math domain error
                term2 = math.sqrt(arg)
                results["V_grad_initial"][direction] = term1 + term2

        # Step 3: Refine radii of curvature and gradient wind speeds
        for direction, V_grad in results["V_grad_initial"].items():
            gamma = angles[direction]
            if V_grad == V_g:
                results["R_t_final"][direction] = results["R_t_initial"][direction]
            else:
                R_t_refined = distance / (1 - (c * math.cos(gamma) / V_grad))
                results["R_t_final"][direction] = R_t_refined

        # Step 4: Recalculate gradient wind speeds with refined radii
        for direction, R_t_final in results["R_t_final"].items():
            if R_t_final == float('inf'):
                results["V_grad_final"][direction] = V_g
            else:
                R_t_m = R_t_final * km_to_m
                term1 = -(f * R_t_m) / 2
                term2 = math.sqrt((f * R_t_m / 2) ** 2 + f * R_t_m * V_g)
                results["V_grad_final"][direction] = term1 + term2

        # Step 5: Calculate fractional errors in gradient wind speeds
        for direction in angles.keys():
            V_grad_initial = results["V_grad_initial"][direction]
            V_grad_final = results["V_grad_final"][direction]
            fractional_error = abs(V_grad_final - V_grad_initial) / V_grad_initial
            results["Fractional_Error"][direction] = fractional_error * 100

        # results["R_t_initial"] = {key: Answer(value, "km", 0) for key, value in results["R_t_initial"].items()}
        # results["V_grad"] = {key: Answer(value, "m/s", 2) for key, value in results["V_grad"].items()}
        # results["R_t_final"] = {key: Answer(value, "km", 0) for key, value in results["R_t_final"].items()}
        # results["Fractional_Error"] = {key: Answer(value, "%", 2) for key, value in results["Fractional_Error"].items()}
        # results = {key: NestedAnswer(value) for key, value in results.items()}

        result_unshown = {
            "R_t_final": {key: value for key, value in results["R_t_final"].items()},
            "V_grad_final": {key: value for key, value in results["V_grad_final"].items()},
        }

        results = {
            "R_t_initial": NestedAnswer({key: Answer(value, "km", 0) for key, value in results["R_t_initial"].items()}),
            "V_grad": NestedAnswer({key: Answer(value, "m/s", 2) for key, value in results["V_grad_initial"].items()}),
            "Fractional_Error": NestedAnswer({key: Answer(value, "%", 2) for key, value in results["Fractional_Error"].items()})
        }
        return NestedAnswer(results)


if __name__ == '__main__':
    q = Question52(unique_id="q")
    print(q.question())
    print(q.answer())