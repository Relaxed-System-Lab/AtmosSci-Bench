import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question53(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """
The mean temperature in the layer between {p1} and {p2} hPa decreases eastward by {temp_gradient}°C per 100 km. 
If the {p1} hPa geostrophic wind is from the southeast at {wind_speed750} m/s, what is the geostrophic wind speed and direction at {p2} hPa? Let f={f} s^-1.
        """
        self.func = self.calculate_geostrophic_wind

        self.default_variables = {
            "p1": 750,  # Initial pressure level (hPa)
            "p2": 500,  # Final pressure level (hPa)
            "temp_gradient": -3.0,  # Temperature gradient (°C per 100 km)
            "wind_speed750": 20.0,  # Geostrophic wind speed at p1 (m/s)
            "wind_dir750": 135.0,  # Geostrophic wind direction at p1 (degrees from north)
            "f": 1e-4,  # Coriolis parameter (s^-1)
        }

        self.constant = {
            "R": 287.0,  # Gas constant for dry air (J/(kg·K))

        }

        self.independent_variables = {
            "p1": {"min": 500, "max": 1000, "granularity": 10},
            "p2": {"min": 500, "max": 1000, "granularity": 10},
            "temp_gradient": {"min": -10.0, "max": 10.0, "granularity": 0.1},
            "wind_speed750": {"min": 5.0, "max": 50.0, "granularity": 0.1},
            "wind_dir750": {"min": 0.0, "max": 360.0, "granularity": 1.0},
        }

        self.dependent_variables = {
            "f": lambda vars: 2 * 7.2921e-5 * math.sin(math.radians(45)),  # Example: latitude dependency
        }

        self.choice_variables = {}

        self.custom_constraints = [
            lambda vars, res: vars["p1"] > vars["p2"],  # Initial pressure must be higher than final pressure
        ]
        super(Question53, self).__init__(unique_id, seed, variables)


    @staticmethod
    def calculate_geostrophic_wind(p1, p2, temp_gradient, wind_speed750, wind_dir750, f, R=287.0):
        """
        Calculate geostrophic wind speed and direction at the target pressure level.

        Parameters:
            p1 (float): Initial pressure level (hPa).
            p2 (float): Target pressure level (hPa).
            temp_gradient (float): Temperature gradient (°C per 100 km).
            wind_speed750 (float): Wind speed at p1 (m/s).
            wind_dir750 (float): Wind direction at p1 (degrees from north).
            f (float): Coriolis parameter (s^-1).
            R (float): Gas constant for dry air (default: 287 J/(kg·K)).

        Returns:
            tuple: (wind_speed, wind_direction) at p2.
        """
        # Convert wind components at p1
        u750 = wind_speed750 * math.cos(math.radians(270 - wind_dir750))
        v750 = wind_speed750 * math.sin(math.radians(270 - wind_dir750))

        # Calculate thermal wind components
        u_T = 0  # Zonal thermal wind component (assumed zero)

        # Convert temperature gradient from °C per 100 km to K/m
        temp_gradient_K_per_m = temp_gradient / 100000

        # Calculate the natural logarithm of the pressure ratio
        ln_pressure_ratio = math.log(p1 / p2)

        # Calculate the thermal wind component
        v_T = -(R / f) * temp_gradient_K_per_m * ln_pressure_ratio

        # Geostrophic wind components at p2
        u500 = u750 + u_T
        v500 = v750 + v_T
        
        print("v750: ", v750)
        print("v_T: ", v_T)

        # # Wind speed and direction
        # wind_speed = math.sqrt(u500**2 + v500**2)
        # wind_direction = (270 - math.degrees(math.atan2(v500, u500))) % 360

        return u500, v500


if __name__ == '__main__':
    q = Question53(unique_id="q")
    print(q.question())
    print(q.answer())