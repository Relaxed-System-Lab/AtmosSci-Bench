import random
from decimal import Decimal


class Answer(object):
    """
    Abstract class for all answers.
    """
    def __init__(self, value, unit="", round=None):
        self.value = value
        self.round = round
        self.unit = unit

        self.is_text = True if isinstance(value, str) else False

    @property
    def rounded_value(self):
        if self.is_text:
            return self.value
        if self.round is None:
            return self.value
        return round(self.value, self.round)

    def __str__(self):
        return f"{self.rounded_value} {self.unit}"

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        return self.__str__() + "; " + other.__str__()

    # === Value Comparison ===
    def __eq__(self, other):
        return self.rounded_value == other

    def __ne__(self, other):
        return self.rounded_value != other

    def __lt__(self, other):
        return self.rounded_value < other

    def __le__(self, other):
        return self.rounded_value <= other

    def __gt__(self, other):
        return self.rounded_value > other

    def __ge__(self, other):
        return self.rounded_value >= other

    # Calculation
    def __mul__(self, other):
        if self.is_text:
            return Answer(self.value, self.unit, self.round)

        if isinstance(other, (int, float, Decimal)):
            new_value = self.value * other
            return Answer(new_value, self.unit, self.round)
        raise TypeError("Multiplication is only supported with numeric types.")




class NestedAnswer(object):
    """
    Abstract class for nested answers.
    """
    def __init__(self, nested_data):
        if not isinstance(nested_data, (dict, list)):
            raise TypeError("nested_data must be a dictionary or a list.")
        self.nested_data = nested_data

    def __str__(self):
        if isinstance(self.nested_data, dict):
            return ",\n".join(f"{k}: {v}" for k, v in self.nested_data.items())
        elif isinstance(self.nested_data, list):
            return ",\n".join(str(v) for v in self.nested_data)

    def __eq__(self, other):
        if not isinstance(other, NestedAnswer):
            raise TypeError("Cannot compare NestedAnswer with non-NestedAnswer object.", self, other)

        if isinstance(self.nested_data, dict):
            return all(key in other.nested_data and self.nested_data[key] == other.nested_data[key]
                       for key in self.nested_data)
        elif isinstance(self.nested_data, list):
            return all(value in other.nested_data for value in self.nested_data)


    # Calculation
    def __mul__(self, other):
        if not isinstance(other, (int, float, Decimal)):
            raise TypeError("Multiplication is only supported with numeric types.")

        if isinstance(self.nested_data, dict):
            new_nested_data = {
                key: (value * other if not isinstance(value, list)
                      else [x * other for x in value])
                for key, value in self.nested_data.items()
            }
        elif isinstance(self.nested_data, list):
            new_nested_data = [
                (value * other if not isinstance(value, list)
                 else [x * other for x in value])
                for value in self.nested_data
            ]
        else:
            raise TypeError("Unsupported type for nested_data.")

        return NestedAnswer(new_nested_data)
