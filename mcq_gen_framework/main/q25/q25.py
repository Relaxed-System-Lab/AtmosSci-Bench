import random, math
from question import Question
from answer import Answer, NestedAnswer


class Question25(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Geophysics"
        self.template = """Currently, the Earth's emission temperature is {current_temp} K, with an albedo of {current_albedo_percent}%. 
What change in the emission temperature would occur if the albedo decreased to {new_albedo_percent}% while keeping all other factors constant?

The emission temperature is given by:

T_e = [(1 - alpha_p) * S / (4 * sigma)]^(1/4)

where alpha_p represents the planetary albedo, $S$ is the solar flux, and $\sigma$ is the Stefan-Boltzmann constant."""
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