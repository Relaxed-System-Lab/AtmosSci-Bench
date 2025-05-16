import random
from question import Question
from answer import Answer, NestedAnswer

class Question2(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """A watershed consists of {open_space_percent}% open space/lawn in good condition, with {open_space_C_percent}% classified as soil group C and {open_space_A_percent}% as soil group A. The remaining {forest_percent}% of the watershed is forest land with fair cover, also in soil group C. The curve numbers (CN) for these soil conditions are provided in the table below. Apply the SCS Method to calculate the excess precipitation given a total rainfall of {rainfall} inches in this watershed. Clearly outline all assumptions. Assume normal antecedent runoff conditions (ARC II) and Ia=0.2S.

| Land use                   | Soil group | CN |
|----------------------------|------------|----|
| Good condition open space/lawn | C      | 74 |
| Good condition open space/lawn | A      | 39 |
| Forest land with fair cover     | C      | 73 |"""
        self.func = self.calculate_excessive_precipitation
        self.default_variables = {
            "open_space_percent": 80,      # % of the watershed as good condition open space
            "open_space_C_percent": 40,   # % of the open space with soil group C
            "open_space_A_percent": 60,   # % of the open space with soil group A
            "forest_percent": 20,         # % of the watershed as forest with soil group C
            "rainfall": 7.0,              # Total rainfall (inches)
        }

        self.independent_variables = {
            "open_space_percent": {"min": 0, "max": 100, "granularity": 1},
            "open_space_C_percent": {"min": 0, "max": 100, "granularity": 1},
            "rainfall": {"min": 0, "max": 100, "granularity": 0.1},
        }

        self.dependent_variables = {
            "forest_percent": lambda vars: 100 - vars["open_space_percent"],
            "open_space_A_percent": lambda vars: 100 - vars["open_space_C_percent"],
        }

        self.choice_variables = {
        }

        self.custom_constraints = [
        ]

        super(Question2, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_excessive_precipitation(
        open_space_percent,
        open_space_C_percent,
        open_space_A_percent,
        forest_percent,
        rainfall
    ):
        """
        Calculate excessive precipitation using the SCS method.

        Parameters:
            open_space_percent (float): Percentage of watershed as open space.
            open_space_C_percent (float): Percentage of open space with soil group C.
            open_space_A_percent (float): Percentage of open space with soil group A.
            forest_percent (float): Percentage of watershed as forest with soil group C.
            rainfall (float): Total rainfall in inches.
            # ia_factor (float): Initial abstraction factor (Ia/S).

        Returns:
            float: Excessive precipitation in inches.
        """
        # Curve numbers for the different land use and soil group combinations
        curve_numbers = {
            ("open_space", "C"): 74,
            ("open_space", "A"): 39,
            ("forest", "C"): 73
        }
        ia_factor = 0.2

        # Calculate the weighted curve number (CN)
        total_area = open_space_percent + forest_percent
        open_space_weight = open_space_percent / total_area
        forest_weight = forest_percent / total_area

        weighted_cn = (
            open_space_weight * (
                open_space_C_percent / 100 * curve_numbers[("open_space", "C")] +
                open_space_A_percent / 100 * curve_numbers[("open_space", "A")]
            ) +
            forest_weight * curve_numbers[("forest", "C")]
        )

        # Calculate potential maximum retention (S)
        S = (1000 / weighted_cn) - 10

        # Calculate excessive precipitation (Pe)
        Pe = (rainfall - ia_factor * S) ** 2 / (rainfall + (1 - ia_factor) * S)

        return Answer(Pe, "in", 2)


if __name__ == '__main__':
    q = Question2(unique_id="q")
    print(q.question())
    print(q.answer())