import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer



class Question6(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
#         self.template = """
# In a circular conduit with varying diameters, diameter D1={D1} m, transitions to D2={D2} m. 
# The velocity at the outlet profile was measured: V2={V2} m/s. 
# Calculate the discharge and the mean velocity at the inlet profile V1. 
# Also, determine the type of flow in both conduit profiles (whether the flow is laminar or turbulent). 
# The kinematic viscosity of water is v={kinematic_viscosity} m²/s.

# ![](https://cdn.mathpix.com/cropped/2024_12_06_b79d610f0ffcf56a3450g-07.jpg?height=227&width=361&top_left_y=766&top_left_x=845)
        # """
        self.template = """
In a circular conduit with varying diameters, diameter D1={D1} m, transitions to D2={D2} m. 
The velocity at the outlet profile was measured: V2={V2} m/s. 
Calculate the discharge and the mean velocity at the inlet profile V1. 
Also, determine the type of flow in both conduit profiles (whether the flow is laminar or turbulent). 
The kinematic viscosity of water is v={kinematic_viscosity} m²/s.
        """
        self.func = self.analyze_flow
        self.default_variables = {
            "D1": 1.5,                  # Diameter at the inlet (m)
            "D2": 2.5,                  # Diameter at the outlet (m)
            "V2": 2.5,                  # Velocity at the outlet (m/s)
            "kinematic_viscosity": 1e-6 # Kinematic viscosity of the fluid (m²/s)
        }
        self.independent_variables = {
            "D1": {"min": 0.1, "max": 5.0, "granularity": 0.1},
            "D2": {"min": 0.1, "max": 5.0, "granularity": 0.1},
            "V2": {"min": 0.1, "max": 10.0, "granularity": 0.1},
            "kinematic_viscosity": {"min": 1e-6, "max": 1e-3, "granularity": 1e-7}
        }

        self.dependent_variables = {}

        self.choice_variables = {
        }

        self.custom_constraints = [
        ]
        super(Question6, self).__init__(unique_id, seed, variables)

    @staticmethod
    def analyze_flow(D1, D2, V2, kinematic_viscosity):
        """
        Analyze the flow in a circular conduit with varying diameters.

        Parameters:
        D1 (float): Diameter at the inlet (m).
        D2 (float): Diameter at the outlet (m).
        V2 (float): Velocity at the outlet (m/s).
        kinematic_viscosity (float): Kinematic viscosity of the fluid (m²/s).

        Returns:
        dict: Contains discharge (Q), velocity at inlet (V1), and flow types at both profiles.
        """
        import math

        # Cross-sectional areas
        A1 = math.pi * (D1 / 2) ** 2  # Area at inlet
        A2 = math.pi * (D2 / 2) ** 2  # Area at outlet

        # Continuity equation: Q = A * V
        Q = A2 * V2  # Discharge is constant, so we calculate it from the outlet values
        V1 = Q / A1  # Velocity at the inlet

        # Calculate Reynolds numbers to determine flow type
        # print("kinematic_viscosity", kinematic_viscosity)
        Re1 = V1 * D1 / kinematic_viscosity  # Reynolds number at the inlet
        Re2 = V2 * D2 / kinematic_viscosity  # Reynolds number at the outlet

        # Determine flow types
        flow_type_inlet = "laminar" if Re1 < 4000 else "turbulent"
        flow_type_outlet = "laminar" if Re2 < 4000 else "turbulent"

        # Return the results as a dictionary
        return NestedAnswer({
            "discharge": Answer(Q, "m^3/s", 3),
            "velocity_inlet": Answer(V1, "m/s", 3),
            "Reynolds_inlet": Answer(Re1, "", 2),
            "Reynolds_outlet": Answer(Re2, "", 2),
            "flow_type_inlet": Answer(flow_type_inlet, "", None),
            "flow_type_outlet": Answer(flow_type_outlet, "", None)
        })

if __name__ == '__main__':
    q = Question6(unique_id="q")
    print(q.question())
    print(q.answer())