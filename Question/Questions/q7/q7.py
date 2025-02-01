import random, math
from ..question import Question
from Questions.answer import Answer


class Question7(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """
A horizontal pipe is made of forged steel. The pipe diameter is {pipe_diameter} m. 
Room temperature water ({fluid_temperature}°C, ρ={fluid_density} kg/m³) is transported for {pipe_length} m in the pipe, 
with a pressure drop of {pressure_drop} Pa over this length. 
The dynamic viscosity of water is {fluid_viscosity} Pa·s, and the pipe roughness is {pipe_roughness} m. 
Calculate the flow rate in the pipe.

![](https://cdn.mathpix.com/cropped/2024_12_06_b79d610f0ffcf56a3450g-08.jpg?height=901&width=1434&top_left_y=492&top_left_x=431)
        """
        self.func = self.calculate_flow_rate
        self.default_variables = {
            "pipe_diameter": 0.4,        # Pipe diameter in meters
            "pipe_length": 500,          # Pipe length in meters
            "pressure_drop": 100000,     # Pressure drop in Pascals
            "fluid_temperature": 23,     # Fluid temperature in °C
            "fluid_density": 997.45,     # Fluid density in kg/m³
            "fluid_viscosity": 0.001,    # Dynamic viscosity in Pa·s
            "pipe_roughness": 0.025   # Pipe roughness in meters
        }

        self.independent_variables = {
            "pipe_diameter": {"min": 0.1, "max": 1.0, "granularity": 0.01},
            "pipe_length": {"min": 1, "max": 1000, "granularity": 1},
            "pressure_drop": {"min": 100, "max": 1000000, "granularity": 100},
            "fluid_temperature": {"min": 0, "max": 100, "granularity": 1},
            "fluid_density": {"min": 500, "max": 1200, "granularity": 1},
            "fluid_viscosity": {"min": 0.0001, "max": 0.01, "granularity": 0.0001},
            "pipe_roughness": {"min": 0.000001, "max": 0.0005, "granularity": 0.000001}
        }

        self.dependent_variables = {}

        self.choice_variables = {
        }

        self.custom_constraints = [
        ]

        super(Question7, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_flow_rate(pipe_diameter, pipe_length, pressure_drop, fluid_density, fluid_viscosity, pipe_roughness, fluid_temperature):
        import math

        # Step 1: Compute relative roughness
        relative_roughness = pipe_roughness / pipe_diameter

        if pipe_diameter <= 0 or fluid_density <= 0 or fluid_viscosity <= 0 or pipe_length <= 0:
            raise ValueError("Input parameters must be positive and non-zero.")

        # Step 2: Define Colebrook-White equation
        def colebrook_white(f, Re, rel_roughness):
            return (-2.0 * math.log10(rel_roughness / 3.7 + 2.51 / (Re * math.sqrt(f)))) - 1.0 / math.sqrt(f)

        # Step 3: Solve friction factor iteratively
        def solve_friction_factor(Re, rel_roughness):
            f_guess = 0.02  # Initial guess
            for _ in range(100):  # Limit iterations to avoid infinite loop
                try:
                    f_new = (-2.0 * math.log10(rel_roughness / 3.7 + 2.51 / (Re * math.sqrt(f_guess)))) ** -2
                except (ValueError, OverflowError) as e:
                    raise ValueError(f"Friction factor calculation failed: {e}")

                if abs(f_new - f_guess) < 1e-6:  # Convergence condition
                    return f_new
                f_guess = f_new

            raise ValueError("Friction factor iteration failed to converge.")

        # Step 4: Velocity and Reynolds number iteration
        velocity = 1  # Initial guess
        for _ in range(100):  # Iterate until convergence
            Re = (fluid_density * velocity * pipe_diameter) / fluid_viscosity
            if Re <= 0:
                raise ValueError("Reynolds number is non-positive, check input parameters.")

            friction_factor = solve_friction_factor(Re, relative_roughness)

            new_velocity = math.sqrt((2 * pressure_drop) / (friction_factor * pipe_length / pipe_diameter * fluid_density))
            if abs(new_velocity - velocity) < 1e-6:  # Convergence condition
                velocity = new_velocity
                break
            velocity = new_velocity

        # Step 5: Calculate flow rate
        cross_sectional_area = math.pi * (pipe_diameter / 2) ** 2
        flow_rate = velocity * cross_sectional_area
        return Answer(flow_rate, "m^3/s", 3)


if __name__ == '__main__':
    q = Question7(unique_id="q")
    print(q.question())
    print(q.answer())