import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question55(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Atmospheric Dynamics"
        self.template = """ 
The planet {planet_name} rotates about its axis so slowly that to a reasonable approximation the Coriolis parameter may be set equal to zero. 
For steady, frictionless motion parallel to latitude circles, the momentum equation (2.20) then reduces to a type of cyclostrophic balance:
u^2 * tan(φ) / a = -(1 / ρ) * (∂p / ∂y). 

By transforming this expression to isobaric coordinates, show that the thermal wind equation in this case can be expressed in the form:
ω_r^2(p1) - ω_r^2(p0) = -(R * ln(p0 / p1)) / (a * sin(φ) * cos(φ)) * (∂⟨T⟩ / ∂y),
where R is the gas constant, a is the radius of the planet, and ω_r ≡ u / (a * cos(φ)) is the relative angular velocity.

How must ⟨T⟩ (the vertically averaged temperature) vary with respect to latitude in order for ω_r to be a function only of pressure? 

If the zonal velocity at about 60 km height above the equator (p1 = {p1} Pa) is {u1} m/s and the zonal velocity vanishes at the surface of the planet (p0 = {p0} Pa), 
what is the vertically averaged temperature difference between the equator and pole, assuming that ω_r depends only on pressure? 
The planetary radius is a = {a} m, and the gas constant is R = {R} J/(kg*K).
        """
        self.func = self.calculate_temperature_difference

        self.default_variables = {
            "planet_name" : "Venus",
            "p1": 2.9e5,  # Pressure at 60 km height (Pa)
            "p0": 9.5e6,  # Pressure at the surface (Pa)
            "a": 6100e3,  # Planetary radius (m)
        }
        self.constant = {
            "R": 187.0,    # Gas constant (J/(kg*K))
            "u1": 100.0,  # Zonal velocity at 60 km height (m/s)
        }

        self.independent_variables = {
        #    "u1": {"min": 50, "max": 150, "granularity": 0.1},
        #    "p1": {"min": 1e5, "max": 5e5, "granularity": 1000},
        #    "p0": {"min": 1e6, "max": 1e7, "granularity": 10000},
        }

        self.dependent_variables = {
        }

        self.choice_variables = {
            "planet": [
                {"planet_name": "Earth", "a": 6371e3, "R": 287.0, "p0": 101325, "p1": 0.0225},
                {"planet_name": "Venus", "a": 6052e3, "R": 187.0, "p0": 9.2e6, "p1": 2.9e5},
                {"planet_name": "Mars", "a": 3389e3, "R": 193.0, "p0": 610, "p1": 0.03},
                {"planet_name": "Jupiter", "a": 69911e3, "R": 3700.0, "p0": 1e5, "p1": 1e3},
                {"planet_name": "Saturn", "a": 58232e3, "R": 3000.0, "p0": 1e5, "p1": 0.7e3},
                {"planet_name": "Titan", "a": 2575e3, "R": 297.0, "p0": 146700, "p1": 320},
                {"planet_name": "Uranus", "a": 25362e3, "R": 3600.0, "p0": 1e5, "p1": 0.3e3},
                {"planet_name": "Neptune", "a": 24622e3, "R": 3800.0, "p0": 1e5, "p1": 0.2e3},
                {"planet_name": "Pluto", "a": 1188e3, "R": 100.0, "p0": 1, "p1": 0.01},
                {"planet_name": "Mercury", "a": 2440e3, "R": 191.0, "p0": 0, "p1": 0},
                {"planet_name": "Ganymede", "a": 2634e3, "R": 296.0, "p0": 1e5, "p1": 0.02},
                {"planet_name": "Europa", "a": 1560e3, "R": 297.0, "p0": 1e4, "p1": 0.1},
                {"planet_name": "Callisto", "a": 2410e3, "R": 296.0, "p0": 1e3, "p1": 0.05},
                {"planet_name": "Io", "a": 1821e3, "R": 300.0, "p0": 1e5, "p1": 0.2},
                {"planet_name": "Triton", "a": 1353e3, "R": 295.0, "p0": 1.2e5, "p1": 0.05},
                {"planet_name": "Eris", "a": 1163e3, "R": 90.0, "p0": 0.1, "p1": 0.001},
                {"planet_name": "Ceres", "a": 473e3, "R": 70.0, "p0": 0.03, "p1": 0.0001},
                {"planet_name": "Haumea", "a": 816e3, "R": 80.0, "p0": 0.1, "p1": 0.01},
                {"planet_name": "Makemake", "a": 715e3, "R": 80.0, "p0": 0.05, "p1": 0.005},
                {"planet_name": "Charon", "a": 606e3, "R": 100.0, "p0": 0.05, "p1": 0.002},
                {"planet_name": "Enceladus", "a": 252e3, "R": 150.0, "p0": 0.1, "p1": 0.01},
                {"planet_name": "Mimas", "a": 198e3, "R": 150.0, "p0": 0.05, "p1": 0.005},
                {"planet_name": "Tethys", "a": 531e3, "R": 150.0, "p0": 0.1, "p1": 0.01},
                {"planet_name": "Rhea", "a": 764e3, "R": 150.0, "p0": 0.1, "p1": 0.01},
                {"planet_name": "Iapetus", "a": 734e3, "R": 150.0, "p0": 0.05, "p1": 0.005},
                {"planet_name": "Phoebe", "a": 107e3, "R": 150.0, "p0": 0.02, "p1": 0.001},
                {"planet_name": "Oberon", "a": 761e3, "R": 150.0, "p0": 0.05, "p1": 0.005},
                {"planet_name": "Titania", "a": 789e3, "R": 150.0, "p0": 0.05, "p1": 0.005},
                {"planet_name": "Umbriel", "a": 584e3, "R": 150.0, "p0": 0.05, "p1": 0.005},
                {"planet_name": "Ariel", "a": 579e3, "R": 150.0, "p0": 0.05, "p1": 0.005},
                {"planet_name": "Miranda", "a": 235e3, "R": 150.0, "p0": 0.05, "p1": 0.005},
                {"planet_name": "Hyperion", "a": 135e3, "R": 150.0, "p0": 0.02, "p1": 0.001},
                {"planet_name": "Dione", "a": 561e3, "R": 150.0, "p0": 0.1, "p1": 0.01},
                {"planet_name": "Theia", "a": 6371e3, "R": 287.0, "p0": 101325, "p1": 0.0225},
                {"planet_name": "Planet X", "a": 10000e3, "R": 287.0, "p0": 101325, "p1": 1e-3},
                {"planet_name": "Proxima b", "a": 6371e3, "R": 287.0, "p0": 101325, "p1": 0.1},
                {"planet_name": "Kepler-22b", "a": 25000e3, "R": 287.0, "p0": 1e5, "p1": 0.1},
                {"planet_name": "Gliese 581g", "a": 15000e3, "R": 287.0, "p0": 1e5, "p1": 1},
                {"planet_name": "TRAPPIST-1e", "a": 7000e3, "R": 287.0, "p0": 101325, "p1": 0.2},
                {"planet_name": "TRAPPIST-1f", "a": 7200e3, "R": 287.0, "p0": 101325, "p1": 0.1},
                {"planet_name": "TOI-700d", "a": 6400e3, "R": 287.0, "p0": 101325, "p1": 0.2},
                {"planet_name": "LHS 1140b", "a": 17300e3, "R": 287.0, "p0": 101325, "p1": 0.01},
            ]
        }


        self.custom_constraints = [
        #    lambda vars, res: vars["p0"] > vars["p1"]
        ]

        super(Question55, self).__init__(unique_id, seed, variables)

    @staticmethod
    def calculate_temperature_difference(u1, p1, p0, a, R, planet_name):
        """
        Calculate the vertically averaged temperature difference between the equator and the pole.
        
        Parameters:
            u1 (float): Zonal velocity at the top layer (m/s).
            p1 (float): Pressure at the top layer (Pa).
            p0 (float): Pressure at the surface (Pa).
            a (float): Radius of the planet (m).
            R (float): Specific gas constant (J/kg/K).

        Returns:
            float: Vertically averaged temperature difference (K).
        """
        # Calculate angular velocity at the top layer
        omega_r1 = u1 / a

        # Difference in angular velocity squared
        omega_diff_squared = omega_r1**2

        # Temperature difference calculation
        T_prime = (omega_diff_squared * a**2) / (2 * R * math.log(p0 / p1))
        return Answer(T_prime, "K", 2)


if __name__ == '__main__':
    q = Question55(unique_id="q")
    print(q.question())
    print(q.answer())