import random
from ..question import Question
from Questions.answer import Answer, NestedAnswer

class Question3(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """
The CN value of a watershed is {CN}, the following table summarizes the rainfall intensity during the storm event. 
Calculate the excessive precipitation for each time step (10 min interval).

| Time | Rainfall Intensity (in/hr) |
| :--- | :--- |
| 0-10min | {intensity1} |
| 10-20min | {intensity2} |
| 20-30min | {intensity3} |
| 30-40min | {intensity4} |
| 40-50min | {intensity5} |
| 50-60min | {intensity6} |
| 60-70min | {intensity7} |
| 70-80min | {intensity8} |
    """
        self.func = self.calculate_excessive_precipitation
        self.default_variables = {
            "intensity1": 2.0,
            "intensity2": 4.5,
            "intensity3": 5.0,
            "intensity4": 9.0,
            "intensity5": 8.0,
            "intensity6": 7.0,
            "intensity7": 3.5,
            "intensity8": 3.0,
            "CN": 57.0,  # Curve Number
        }
        self.independent_variables = {
            "intensity1": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "intensity2": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "intensity3": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "intensity4": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "intensity5": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "intensity6": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "intensity7": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "intensity8": {"min": 0.0, "max": 10.0, "granularity": 0.1},
            "CN": {"min": 30.0, "max": 100.0, "granularity": 1.0}
        }

        self.dependent_variables = {

        }

        self.choice_variables = {
        }

        self.custom_constraints = [
        ]

        super(Question3, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_excessive_precipitation(
        intensity1, intensity2, intensity3, intensity4, intensity5, intensity6, intensity7, intensity8, CN
    ):
        """
        Calculate the excessive precipitation for each time step using the CN model.
        """
        rainfall_data = {
            "0-10min": intensity1,
            "10-20min": intensity2,
            "20-30min": intensity3,
            "30-40min": intensity4,
            "40-50min": intensity5,
            "50-60min": intensity6,
            "60-70min": intensity7,
            "70-80min": intensity8,
        }

        S = 1000 / CN - 10
        Ia = 0.2 * S

        time_step_minutes = 10
        time_step_hours = time_step_minutes / 60
        cumulative_rainfall = 0
        excessive_precipitation = {}

        for interval, intensity in rainfall_data.items():
            rainfall = intensity * time_step_hours
            cumulative_rainfall += rainfall

            if cumulative_rainfall < Ia:
                Pe = 0
            else:
                Pe = ((cumulative_rainfall - Ia) ** 2) / (cumulative_rainfall + 0.8 * S)

            excessive_precipitation[interval] = Answer(Pe, "in", 4)

        return NestedAnswer(excessive_precipitation)


if __name__ == '__main__':
    q = Question3(unique_id="q")
    print(q.question())
    print(q.answer())