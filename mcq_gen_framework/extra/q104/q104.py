import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question104(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """Consider two "streamtube" segments within a catchment area—essentially parts of a flow net defined by topography—with the following characteristics:

|  | Segment 1 | Segment 2 |
| :--- | :--- | :--- |
| Upslope area, A (m²) | {A1} | {A2} |
| Length of contour at the segment's base, c (m) | {c1} | {c2} |
| Slope at the segment's base, tanβ | {tanb1} | {tanb2} |

Determine the topographic index for each segment and specify which segment is more prone to generating saturation-excess overland flow."""

        self.func = self.calculate_topographic_index

        self.default_variables = {
            "A1": 500.0,
            "A2": 500.0,
            "c1": 3.5,
            "c2": 25.0,
            "tanb1": 0.02,
            "tanb2": 0.08
        }

        self.constant = {}

        self.independent_variables = {
            "A1": {"min": 100.0, "max": 1000.0, "granularity": 10.0},
            "A2": {"min": 100.0, "max": 1000.0, "granularity": 10.0},
            "c1": {"min": 1.0, "max": 10.0, "granularity": 0.1},
            "c2": {"min": 10.0, "max": 50.0, "granularity": 0.5},
            "tanb1": {"min": 0.01, "max": 0.05, "granularity": 0.005},
            "tanb2": {"min": 0.05, "max": 0.1, "granularity": 0.005}
        }

        self.dependent_variables = {}

        self.choice_variables = {
            "segment_examples": [
                {
                    "A1": 500.0, "A2": 500.0,
                    "c1": 3.5, "c2": 25.0,
                    "tanb1": 0.02, "tanb2": 0.08
                },
                {
                    "A1": 800.0, "A2": 600.0,
                    "c1": 4.0, "c2": 30.0,
                    "tanb1": 0.015, "tanb2": 0.09
                }
            ]
        }

        self.custom_constraints = [
            lambda vars, res: vars["tanb1"] > 0 and vars["tanb2"] > 0,
        ]

        super(Question104, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_topographic_index(A1, A2, c1, c2, tanb1, tanb2):
        """
        Calculates the topographic index for two streamtube segments.
        Returns:
            (TI1, TI2, likely_segment_index): TI values for each segment and the one more likely to produce saturation-excess flow.
        """
        # Topographic Index: TI = ln[(A/c) / tan(beta)]
        TI1 = math.log((A1 / c1) / tanb1)
        TI2 = math.log((A2 / c2) / tanb2)
        likely_segment = 1 if TI1 > TI2 else 2
        return NestedAnswer({
            "TI1": Answer(TI1, "", 2),
            "TI2": Answer(TI2, "", 2),
            "likely_segment": Answer(likely_segment, "", None)
        })


if __name__ == '__main__':
    q = Question104(unique_id="q")
    print(q.question())
    print(q.answer())