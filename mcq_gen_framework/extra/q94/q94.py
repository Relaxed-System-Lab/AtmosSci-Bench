import random, math
from question import Question
from answer import Answer, NestedAnswer
import numpy as np

class Question94(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Hydrology"
        self.template = """Two tipping bucket rain gauges are utilized to record the following rainfall data:

| Time | Cumulative precipitation (mm) at Station#1 | Cumulative precipitation (mm) at Station#2 |
| :--- | :--- | :--- |
| 4:00 a.m. | {p1_1} | {p2_1} |
| 6:00 a.m. | {p1_2} | {p2_2} |
| 8:00 a.m. | {p1_3} | {p2_3} |
| 10:00 a.m. | {p1_4} | {p2_4} |
| 12:00 noon | {p1_5} | {p2_5} |
| 2:00 p.m. | {p1_6} | {p2_6} |
| 4:00 p.m. | {p1_7} | {p2_7} |
| 6:00 p.m. | {p1_8} | {p2_8} |
| 8:00 p.m. | {p1_9} | {p2_9} |
| 10:00 p.m. | {p1_10} | {p2_10} |
| 12:00 midnight | {p1_11} | {p2_11} |
| 2:00 a.m. | {p1_12} | {p2_12} |
| 4:00 a.m. | {p1_13} | {p2_13} |

(a) Determine the average daily rainfall intensity for each station (mm/hr).
(b) Determine the peak 2-hour rainfall intensity for each station (mm/hr).
(c) Determine the peak 6-hour rainfall intensity for each station (mm/hr).
(d) Using the arithmetic mean method and given that the drainage basin covers an area of {basin_area} mi², compute the total rainfall volume (m³) that reached the basin during the event."""

        self.func = self.calculate_rainfall_metrics

        self.default_variables = {
            "p1_1": 0.0,
            "p1_2": 0.0,
            "p1_3": 1.0,
            "p1_4": 4.0,
            "p1_5": 13.0,
            "p1_6": 17.0,
            "p1_7": 19.0,
            "p1_8": 19.0,
            "p1_9": 19.0,
            "p1_10": 19.0,
            "p1_11": 19.0,
            "p1_12": 19.0,
            "p1_13": 19.0,

            "p2_1": 0.0,
            "p2_2": 0.0,
            "p2_3": 1.0,
            "p2_4": 3.0,
            "p2_5": 11.0,
            "p2_6": 15.0,
            "p2_7": 16.0,
            "p2_8": 17.0,
            "p2_9": 17.0,
            "p2_10": 17.0,
            "p2_11": 17.0,
            "p2_12": 17.0,
            "p2_13": 17.0,

            "basin_area": 176
        }

        # Only the first value is independently sampled; others are dependent on previous timestep
        self.independent_variables = {
            "p1_1": {"min": 0.0, "max": 2.0, "granularity": 0.1},
            "p2_1": {"min": 0.0, "max": 2.0, "granularity": 0.1},
            "basin_area": {"min": 50, "max": 500, "granularity": 1}
        }

        # Recursive dependencies: p1_2 = p1_1 + rand, p1_3 = p1_2 + rand, etc.
        self.dependent_variables = {
            **{f"p1_{i}": (lambda i: lambda vars: vars[f"p1_{i-1}"] + random.uniform(0, 5))(i)
            for i in range(2, 14)},
            **{f"p2_{i}": (lambda i: lambda vars: vars[f"p2_{i-1}"] + random.uniform(0, 5))(i)
            for i in range(2, 14)},
        }

        self.choice_variables = {}

        self.constant = {

        }

        self.custom_constraints = [
            lambda vars, res: all(vars[f"p1_{i}"] <= vars[f"p1_{i+1}"] for i in range(1, 13)),
            lambda vars, res: all(vars[f"p2_{i}"] <= vars[f"p2_{i+1}"] for i in range(1, 13))
        ]

        super(Question94, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_rainfall_metrics(
        p1_1, p1_2, p1_3, p1_4, p1_5, p1_6, p1_7, p1_8, p1_9, p1_10, p1_11, p1_12, p1_13,
        p2_1, p2_2, p2_3, p2_4, p2_5, p2_6, p2_7, p2_8, p2_9, p2_10, p2_11, p2_12, p2_13,
        basin_area
    ):
        """
        Compute:
        A. Mean daily rainfall intensity for each station
        B. Maximum 2-hour rainfall intensity for each station
        C. Maximum 6-hour rainfall intensity for each station
        D. Total rainfall volume delivered to the basin
        """

        from datetime import datetime

        # Time points in hours since 4:00 AM
        time_labels = ["4:00AM", "6:00AM", "8:00AM", "10:00AM", "12:00PM", "2:00PM", "4:00PM",
                    "6:00PM", "8:00PM", "10:00PM", "12:00AM", "2:00AM", "4:00AM"]
        base_time = datetime.strptime(time_labels[0], '%I:%M%p')
        times = [(datetime.strptime(t, '%I:%M%p') - base_time).total_seconds() / 3600 for t in time_labels]

        # Reconstruct precipitation lists
        precip1 = [p1_1, p1_2, p1_3, p1_4, p1_5, p1_6, p1_7, p1_8, p1_9, p1_10, p1_11, p1_12, p1_13]
        precip2 = [p2_1, p2_2, p2_3, p2_4, p2_5, p2_6, p2_7, p2_8, p2_9, p2_10, p2_11, p2_12, p2_13]

        def mean_intensity(data):
            return data[-1] / 24  # total over 24 hours

        def max_interval_intensity(data, interval_hr):
            max_i = 0
            for i in range(len(data)):
                for j in range(i + 1, len(data)):
                    dt = times[j] - times[i]
                    if abs(dt - interval_hr) < 1e-3:
                        max_i = max(max_i, (data[j] - data[i]) / interval_hr)
            return max_i

        # A. Mean daily rainfall intensity
        mean1 = mean_intensity(precip1)
        mean2 = mean_intensity(precip2)

        # B. Max 2-hour rainfall intensity
        max2hr_1 = max_interval_intensity(precip1, 2)
        max2hr_2 = max_interval_intensity(precip2, 2)

        # C. Max 6-hour rainfall intensity
        max6hr_1 = max_interval_intensity(precip1, 6)
        max6hr_2 = max_interval_intensity(precip2, 6)

        # D. Total rainfall volume (m³)
        avg_mm = (precip1[-1] + precip2[-1]) / 2
        area_m2 = basin_area * 2.59e6  # convert mi² to m²
        volume_m3 = area_m2 * (avg_mm / 1000)

        return NestedAnswer({
            "(a)": NestedAnswer([Answer(mean1, "mm/hr", 3), Answer(mean2, "mm/hr", 3)]),
            "(b)": NestedAnswer([Answer(max2hr_1, "mm/hr", 2), Answer(max2hr_2, "mm/hr", 2)]),
            "(c)": NestedAnswer([Answer(max6hr_1, "mm/hr", 2), Answer(max6hr_2, "mm/hr", 2)]),
            "(d)": Answer(volume_m3, "m^3", 0)
        })

if __name__ == '__main__':
    q = Question94(unique_id="q")
    print(q.question())
    print(q.answer())