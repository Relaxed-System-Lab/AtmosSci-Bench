import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question25(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Geophysics"
        self.template = """
At present the emission temperature of the Earth is {current_temp} K , and its albedo is {current_albedo_percent}%. 
How would the emission temperature change if the albedo were reduced to {new_albedo_percent}% (and all else were held fixed)?

The emission temperature is defined as:

T_e = [(1 - alpha_p) * S / (4 * sigma)]^(1/4)

where alpha_p is the planetary albedo, $S$ the solar flux, and $\sigma$ the StefanBoltzmann constant.
        """
        self.func = self.calculate_emission_temperature_change
        self.default_variables = {
            "current_temp": 255.0,  # Current emission temperature (K)
            "current_albedo_percent": 30.0,  # Current planetary albedo (% as fraction of 100)
            "new_albedo_percent": 10.0,  # New planetary albedo (% as fraction of 100)
        }
        self.independent_variables = {
            "current_temp": {"min": 200.0, "max": 300.0, "granularity": 0.1},
            "current_albedo_percent": {"min": 0.0, "max": 50.0, "granularity": 0.1},
            "new_albedo_percent": {"min": 0.0, "max": 50.0, "granularity": 0.1},
        }
        self.dependent_variables = {}
        self.choice_variables = {}
        self.custom_constraints = [
                lambda vars, res: vars["new_albedo_percent"] < vars["current_albedo_percent"]
        ]

        super(Question25, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_emission_temperature_change(current_temp, current_albedo_percent, new_albedo_percent):
        """
        Calculate the emission temperature change of Earth due to changes in albedo.

        Parameters:
            current_temp (float): Current emission temperature (K).
            current_albedo_percent (float): Current planetary albedo (% as fraction of 100).
            new_albedo_percent (float): New planetary albedo (% as fraction of 100).

        Returns:
            float: New emission temperature (K).
        """
        current_albedo = current_albedo_percent / 100.0
        new_albedo = new_albedo_percent / 100.0

        # Calculate the ratio of the new emission temperature to the current temperature
        temp_ratio = ((1 - new_albedo) / (1 - current_albedo)) ** 0.25

        # Calculate the new emission temperature
        new_temp = current_temp * temp_ratio

        return Answer(new_temp, "K", 1)



if __name__ == '__main__':
    q = Question25(unique_id="q")
    print(q.question())
    print(q.answer())