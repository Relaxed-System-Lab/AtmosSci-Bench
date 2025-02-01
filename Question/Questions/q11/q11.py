import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question11(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
A block of mass {mass_block} kg is suspended from the end of a weightless string. 
The other end of the string is passed through a small hole in a horizontal platform 
and a ball of mass {mass_ball} kg is attached. At what angular velocity must the ball 
rotate on the horizontal platform to balance the weight of the block if the horizontal 
distance of the ball from the hole is {initial_radius} m? While the ball is rotating, 
the block is pulled down {height_change} m. What is the new angular velocity of the ball? 
How much work is done in pulling down the block?
        """
        self.func = self.calculate_motion
        self.default_variables = {
            "mass_block": 1.0,  # Mass of the suspended block (kg)
            "mass_ball": 10.0,  # Mass of the rotating ball (kg)
            "initial_radius": 1.0,  # Initial horizontal distance of the ball (m)
            "final_radius": 0.9,  # Final horizontal distance of the ball (m)
            "height_change": -0.1  # Vertical displacement of the block (m, negative for downward)
        }
        self.independent_variables = {
            "mass_block": {"min": 0.1, "max": 20.0, "granularity": 0.1},
            "mass_ball": {"min": 0.1, "max": 50.0, "granularity": 0.1},
            "initial_radius": {"min": 0.1, "max": 10.0, "granularity": 0.1},
            "final_radius": {"min": 0.1, "max": 10.0, "granularity": 0.1},
            "height_change": {"min": -5.0, "max": 5.0, "granularity": 0.01}
        }

        self.dependent_variables = {}

        self.choice_variables = {}

        self.custom_constraints = [
                lambda vars, res: vars["mass_block"] < vars["mass_ball"]
        ]

        super(Question11, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_motion(mass_block, mass_ball, initial_radius, final_radius, height_change):
        """
        Calculate the angular velocity and work done in a rotational system with a suspended block.

        Parameters:
            mass_block (float): Mass of the suspended block (kg).
            mass_ball (float): Mass of the rotating ball (kg).
            initial_radius (float): Initial horizontal distance of the ball from the hole (m).
            final_radius (float): Final horizontal distance of the ball from the hole (m).
            height_change (float): Vertical displacement of the block (m).
            
        Returns:
            dict: Initial angular velocity (omega_e), final angular velocity (omega_f), and work done (delta_W).
        """
        import math

        # Initial angular velocity
        omega_e = math.sqrt((mass_block * 9.8) / (mass_ball * initial_radius))
        
        # Final angular velocity using conservation of angular momentum
        omega_f = omega_e * (initial_radius**2 / final_radius**2)
        
        # Change in kinetic energy
        delta_K = (mass_ball / 2) * ((omega_f * final_radius)**2 - (omega_e * initial_radius)**2)
        
        # Change in potential energy
        delta_P = mass_block * 9.8 * height_change
        
        # Total work done
        delta_W = delta_K + delta_P
        
        return NestedAnswer({
            "initial_angular_velocity": Answer(omega_e, "s", 1),
            "final_angular_velocity": Answer(omega_f, "s^-1", 3),
            "work_done": Answer(delta_W, "J", 2)
        })


if __name__ == '__main__':
    q = Question11(unique_id="q")
    print(q.question())
    print(q.answer())