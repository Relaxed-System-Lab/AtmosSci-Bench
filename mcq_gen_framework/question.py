import random
from decimal import Decimal
from answer import Answer, NestedAnswer
from utils import get_original_precision_granularity

DEBUG = False

# enable generate high precision granularity

# PRECISION = "original"
PRECISION = "preset"
# PRECISION = "ultra"


class Question(object):
    """
    Abstract class for all questions.
    """
    def __init__(self, unique_id=None, seed=None, variables=None):
        if DEBUG:
            print(f"\n=== Init Question {unique_id} {seed} ===")

        self.original_question = False
        self.attempt = 0
        self.error = None

        # Set Seed; Determine original question
        if seed is None:  # If no seed is provided, use fixed default value
            self.variables = self.default_variables
            self.original_question = True
            self.seed = 100
        else:
            self.seed = seed

        question_id = int(unique_id[1:]) # remove the first letter "q"
        self.seed = self.seed + question_id**2   # Plus question_id to avoid the same seed
        self.id = unique_id if unique_id else f"q_{self.seed}"
        self.gpt = False
        self.options_types = []

        # for options generation
        self.saved_options = None

        # If constant is not set, initialize to empty dict
        if not hasattr(self, 'constant'):
            self.constant = {}

        if not self.original_question:
            # Set random seed
            random.seed(self.seed)

            if DEBUG:
                print("== Start generating variables ==")

            # Randomly generate initial variable values according to constraints
            self.variables = self._generate_valid_variables(
                self.default_variables, self.independent_variables, self.dependent_variables, self.choice_variables, self.custom_constraints
            )

            if DEBUG:
                print("== Final generated variables: ", self.variables)

        # generate options
        self.options()

    def _generate_random_value(self, constraint):
        """
        Randomly generate variable values according to constraints
        :param constraint: dict, includes min, max, granularity
        :return: float/int, generated value
        """
        min_val = constraint["min"]
        max_val = constraint["max"]
        granularity = constraint["granularity"]

        # doesn't change precision if fixed_precision is True
        fixed_precision = False
        if "fixed_precision" in constraint:
            fixed_precision = constraint["fixed_precision"]

        # enable generate original precision granularity
        if PRECISION == "original" and not fixed_precision:
            if max_val > 0:
                granularity = get_original_precision_granularity(max_val)
                min_val = (-1 if min_val < 0 else 1) * granularity
            else:
                granularity = get_original_precision_granularity(min_val)
                max_val = (-1 if max_val < 0 else 1) * granularity
        elif PRECISION == "ultra" and not fixed_precision:
            granularity = granularity / (10**10)

        # Ensure granularity is valid
        if granularity <= 0:
            raise ValueError("Granularity must be greater than 0.")

        # Compute range and generate random value
        scaled_min = int(min_val / granularity)
        scaled_max = int(max_val / granularity)
        random_scaled_value = random.randint(scaled_min, scaled_max)
        result = random_scaled_value * granularity

        # Fix float precision
        # precision = len(str(granularity).split(".")[1]) if "." in str(granularity) else 0 # cannot solve 1e-7
        precision = abs(Decimal(str(granularity)).as_tuple().exponent)

        return round(result, precision)

    def _generate_valid_variables(self, variables, independent_variables, dependent_variables, choice_variables, custom_constraints):
        """
        Attempt to generate variables multiple times until all constraints are satisfied
        :param variables: dict, default variable values
        :param independent_variables: dict, constraints for each variable
        :param choice_variables: dict, group constraints
        :param custom_constraints: list, custom constraint functions
        :return: dict, variables that satisfy all constraints
        """
        for i in range(1000):  # Try up to 1000 times
            # attempt records the number of attempts
            self.attempt = i

            result = {}

            # Randomly generate independent variables
            for key in independent_variables.keys():
                result[key] = self._generate_random_value(independent_variables[key])

            # Generate dependent variables
            for key, gen_func in dependent_variables.items():
                result[key] = gen_func(result)

            # Apply group constraints
            for group_name, group_values in choice_variables.items():
                selected_group = random.choice(group_values)
                result.update(selected_group)

            # Validate custom constraints
            try:
                res = self.calculate(**result)
            except Exception as e:
                if False:
                    print(f"\s Question{self.id} Generate {i} round failed, retrying...", e)
                continue

            if all(constraint(result, res) for constraint in custom_constraints):
                if DEBUG:
                    print("== Variables generated successfully ==")
                return result

        raise RuntimeError("Unable to generate valid variables after 100 attempts.")

    def calculate(self, **kwargs):
        """
        Compute the answer to the question
        """
        if self.constant:
            kwargs.update(self.constant)

        if DEBUG:
            print("== Calculating: ", kwargs)

        return self.func(**kwargs)

    def display_variables(self):
        """
        Print current variable values
        """
        print(self.variables)

    def question(self):
        """
        Return the question string
        """
        variables = self.variables
        variables.update(self.constant)
        return self.template.format(**variables)

    def question_md(self):
        """
        Return the question string with variables highlighted in red
        """
        # Use HTML tag <font color='red'> to highlight in red
        # Assume self.variables is a dict, e.g., {"var1": "value1", "var2": "value2"}
        highlighted_variables = {
            k: f"<font color='red'>{v} ({k})</font>"
            for k, v in self.variables.items()
        }
        highlighted_variables.update({k: f"<font color='brown'>{v} ({k})</font>"
                                      for k, v in self.constant.items()})

        # Replace template placeholders with highlighted content
        return self.template.format(**highlighted_variables)

    def answer(self, variables=None):
        """
        Return the answer to the question
        """
        if variables is not None:
            variables = variables
        else:
            variables = self.variables

        answer = self.calculate(**variables)

        return answer

    # def generate_variant(self):
    #     """
    #     Generate a new question based on independent_variables
    #     """
    #     if hasattr(self, "independent_variables"):
    #         for key in self.variables.keys():
    #             self.variables[key] = self._generate_random_value(self.independent_variables[key])

    def options(self):
        """
        Return the options for the question
        """
        if DEBUG:
            print("== Generating options ==")

        if self.saved_options is not None:
            return self.saved_options

        random.seed(self.seed)

        def _verify_distracted_answer(options, distracted_answer):
            """
            Verify that the options (could be dict) are valid
            """
            def _verify_single_answer(options, distracted_answer):
                """
                Verify that the single answer is valid
                """
                if str(distracted_answer) in [str(opt) for opt in options]:
                    return False
                if str(distracted_answer) == 0:
                    return False
                return True

            return _verify_single_answer(options, distracted_answer)

        options = []

        # 1. Correct option
        correct_answer = self.answer()
        options.append(correct_answer)

        # 2. Diffusion: swap variables
        random.seed(self.seed)
        diffused_unsuccessful_rate = 2
        diffused_unsuccessful = False
        try:
            keys = list(self.variables.keys())
            values = list(self.variables.values())
            # Shuffle the values until they are different from the original values
            for i in range(20):
                random.shuffle(values)
                if values != list(self.variables.values()):
                    break
                if i == 19:
                    raise RuntimeError("Unable to generate diffused variables after 20 attempts.")
            diffused_variables = dict(zip(keys, values))

            diffused_answer = self.answer(diffused_variables)

            if not _verify_distracted_answer(options, diffused_answer):
                raise RuntimeError("Diffused answer is not valid.")

        except Exception as e:
            diffused_answer = correct_answer * diffused_unsuccessful_rate
            diffused_unsuccessful = True

        options.append(diffused_answer)

        # 3. Confusion: randomly change some variables
        random.seed(self.seed)
        confused_variables = self.variables.copy()
        for key in confused_variables.keys():
            if isinstance(confused_variables[key], str):
                continue
            if random.random() < 0.5:
                random.seed(self.seed)
                confused_variables[key] = confused_variables[key] * random.choice([0.1, 0.5, 1.5, 2, 2.5, 3])

        confused_unsuccessful_rate = 3
        confused_unsuccessful = False

        try:
            confused_answer = self.answer(confused_variables)

            if not _verify_distracted_answer(options, confused_answer):
                confused_answer = correct_answer * confused_unsuccessful_rate
                confused_unsuccessful = True

        except Exception as e:
            confused_answer = correct_answer * confused_unsuccessful_rate
            confused_unsuccessful = True

        options.append(confused_answer)

        # 4. Randomly generated using different seed
        random.seed(self.seed)
        random.seed(random.randint(0, 1000000))
        random_variables = self._generate_valid_variables(
                self.default_variables, self.independent_variables, self.dependent_variables, self.choice_variables, self.custom_constraints
            )
        random_answer = self.calculate(**random_variables)

        random_unsuccessful_rate = 4
        random_unsuccessful = False

        if not _verify_distracted_answer(options, random_answer):
            random_answer = correct_answer * random_unsuccessful_rate
            random_unsuccessful = True

        options.append(random_answer)

        random.seed(self.seed)
        random.shuffle(options)

        def _letter_options(answer):
            options.index(answer)
            return chr(ord('A') + options.index(answer))

        correct_option = _letter_options(correct_answer)

        self.options_types = [{"type": "correct_answer", "option": _letter_options(correct_answer)}, {"type": f"X{diffused_unsuccessful_rate} (diffused_unsuccessful)" if diffused_unsuccessful else "diffused_answer", "option": _letter_options(diffused_answer)}, {"type": f"X{confused_unsuccessful_rate} (confused_unsuccessful)" if confused_unsuccessful else "confused_answer", "option": _letter_options(confused_answer)}, {"type": f"X{random_unsuccessful_rate} (random_unsuccessful)" if random_unsuccessful else "random_answer", "option": _letter_options(random_answer)}]

        self.saved_options = {"options": options, "correct_option": correct_option}

        return self.saved_options

    def options_md(self, show_correct_option=False):
        options = self.options()

        options_str = ""
        for i, option in enumerate(options["options"]):
            options_str += f"{chr(ord('A') + i)}. {option}\n"

        if show_correct_option:
            options_str += f"\nCorrect answer: {options['correct_option']}"

        return options_str

    def options_str_list(self):
        options = self.options()

        return [str(opt) for opt in options["options"]]

    def correct_option(self):
        options = self.options()
        return options["correct_option"]
    
    def options_types_str(self):
        options_types_str = " | ".join(
            f"{note['type']}: {note['option']}" for note in self.options_types
        )
        return options_types_str
