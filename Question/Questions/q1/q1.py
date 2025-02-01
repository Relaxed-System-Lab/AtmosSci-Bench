import random
from Questions.question import Question
from Questions.answer import Answer, NestedAnswer

class Question1(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        """
               
        :param seed: int,      ，          
        """
        self.type = "Hydrology"
        self.template ="""The initial rate of infiltration of a watershed is estimated as {f0} cm/hr, the final capacity is {fc} cm/hr, and the time constant, k is {k} hr^-1. Assume rainfall intensity is always excessive, use Horton's equation to find

(1) The infiltration capacity at t={t1} hr and t={t2} hr;

(2) The total volume of infiltration between t={t1} hr and t={t2} hr.
        """
        self.func = self.calculate_infiltration

        self.default_variables = {
            "f0": 8.0,  # Initial rate of infiltration (cm/hr)
            "fc": 0.5,  # Final infiltration capacity (cm/hr)
            "k": 0.4,   # Time constant (hr^-1)
            "t1": 2.0,  # Start time (hr)
            "t2": 5.0   # End time (hr)
        }

        self.independent_variables = {
            "f0": {"min": 0.1, "max": 20.0, "granularity": 0.1},
            "fc": {"min": 0.1, "max": 5.0, "granularity": 0.1},
            "k": {"min": 0.01, "max": 1.0, "granularity": 0.01},
            "t1": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "t2": {"min": 0.0, "max": 10.0, "granularity": 0.1}
        }

        self.dependent_variables = {}

        self.choice_variables = {
        }

        self.custom_constraints = [
            lambda vars, res: vars["t1"] < vars["t2"]
        ]


        #          
        super(Question1, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_infiltration(f0, fc, k, t1, t2):
        import math

        def infiltration_capacity(f0, fc, k, t):
            return fc + (f0 - fc) * math.exp(-k * t)

        def cumulative_infiltration(f0, fc, k, t):
            return fc * t + ((f0 - fc) / k) * (1 - math.exp(-k * t))

        infiltration_capacity_t1 = infiltration_capacity(f0, fc, k, t1)
        infiltration_capacity_t2 = infiltration_capacity(f0, fc, k, t2)
        total_volume = cumulative_infiltration(f0, fc, k, t2) - cumulative_infiltration(f0, fc, k, t1)

        return NestedAnswer({
            "(1)": NestedAnswer([Answer(infiltration_capacity_t1, "cm/hr", 3), Answer(infiltration_capacity_t2, "cm/hr", 3)]),
            "(2)": Answer(total_volume, "cm", 3)
        })


if __name__ == '__main__':
    #     seed，      x=1, y=2
    q1_1 = Question1(unique_id="q1_1")
    print(q1_1.question())  #   : calculate 1 + 2
    print(q1_1.answer())  #   : 3

    #    seed，      
    q1_2 = Question1(seed=92299999920, unique_id="q1_2")
    print(q1_2.question())
    print(q1_2.answer())

    q1_2 = Question1(seed=999, unique_id="q1_3")
    print(q1_2.question())
    print(q1_2.answer())

    # q1_2.generate_variant()
    # print(q1_2.question())  #     ，  : calculate 3 + 4.7
    # print(q1_2.answer())  #     : 7.7
