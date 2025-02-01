import random, math
from ..question import Question
from Questions.answer import Answer, NestedAnswer


class Question27(Question):
    def __init__(self, unique_id, seed=None, variables=None):
        self.type = "Geophysics"
        self.template = """3. Consider the thermal balance of {planet_name}. You will need the following information about {planet_name}: mean planetary radius = {planetary_radius_km} km; mean radius of orbit around the Sun = {orbit_radius_au} A.U. (where 1 A.U. is the mean radius of the Earth's orbit); planetary albedo = {albedo}.

(a) Assuming a balance between incoming and outgoing radiation, calculate the emission temperature for {planet_name}. 

(b) In fact, {planet_name} has an internal heat source resulting from continued planetary contraction. Using the conventional definition of emission temperature T_e, σ T_e^4 = (outgoing flux of planetary radiation per unit surface area) the measured emission temperature of {planet_name} is {actual_emission_temp} K. Calculate the magnitude of {planet_name}'s internal heat source.

(c) It is believed that the source of Q on {planet_name} is the release of gravitational potential energy by a slow contraction of the planet. On the simplest assumption that {planet_name} is of uniform density and remains so as it contracts, calculate the annual change in its radius a_{planet_name} required to produce your value of Q. (Only one half of the released gravitational energy is convertible to heat, the remainder appearing as the additional kinetic energy required to preserve the angular momentum of the planet.)
        """

        self.func = self.jupiter_thermal_balance

        self.default_variables = {
            "planet_name": "Jupiter",
            "planetary_radius_km": 69500,
            "orbit_radius_au": 5.19,
            "albedo": 0.51,
            "actual_emission_temp": 130,
            "planet_mass": 2e27
        }

        self.independent_variables = {}

        self.constant = {
            "solar_flux_earth": 1367,  # Solar flux at Earth's orbit (W/m^2)
            "gravitational_constant": 6.7e-11  # Gravitational constant (m^3/kg/s^2)
        }

        self.dependent_variables = {}

        self.choice_variables = {
            "planet": [
                {"planet_name": "Mercury", "planetary_radius_km": 2440, "orbit_radius_au": 0.39, "albedo": 0.12, "planet_mass": 3.3e23, "actual_emission_temp": 440},
                {"planet_name": "Venus", "planetary_radius_km": 6052, "orbit_radius_au": 0.72, "albedo": 0.75, "planet_mass": 4.87e24, "actual_emission_temp": 230},
                {"planet_name": "Earth", "planetary_radius_km": 6371, "orbit_radius_au": 1.0, "albedo": 0.3, "planet_mass": 5.97e24, "actual_emission_temp": 255},
                {"planet_name": "Mars", "planetary_radius_km": 3389, "orbit_radius_au": 1.52, "albedo": 0.25, "planet_mass": 6.42e23, "actual_emission_temp": 210},
                {"planet_name": "Jupiter", "planetary_radius_km": 69500, "orbit_radius_au": 5.19, "albedo": 0.51, "planet_mass": 2e27, "actual_emission_temp": 130},
                {"planet_name": "Saturn", "planetary_radius_km": 58232, "orbit_radius_au": 9.58, "albedo": 0.47, "planet_mass": 5.68e26, "actual_emission_temp": 95},
                {"planet_name": "Uranus", "planetary_radius_km": 25362, "orbit_radius_au": 19.22, "albedo": 0.51, "planet_mass": 8.68e25, "actual_emission_temp": 59},
                {"planet_name": "Neptune", "planetary_radius_km": 24622, "orbit_radius_au": 30.05, "albedo": 0.41, "planet_mass": 1.02e26, "actual_emission_temp": 59},
                {"planet_name": "Pluto", "planetary_radius_km": 1188, "orbit_radius_au": 39.48, "albedo": 0.49, "planet_mass": 1.31e22, "actual_emission_temp": 44},
                {"planet_name": "Moon", "planetary_radius_km": 1737, "orbit_radius_au": 0.00257, "albedo": 0.12, "planet_mass": 7.35e22, "actual_emission_temp": 220},
                {"planet_name": "Europa", "planetary_radius_km": 1560, "orbit_radius_au": 5.2, "albedo": 0.67, "planet_mass": 4.8e22, "actual_emission_temp": 103},
                {"planet_name": "Titan", "planetary_radius_km": 2575, "orbit_radius_au": 9.58, "albedo": 0.22, "planet_mass": 1.35e23, "actual_emission_temp": 93},
                {"planet_name": "Io", "planetary_radius_km": 1821.6, "orbit_radius_au": 5.2, "albedo": 0.63, "planet_mass": 8.93e22, "actual_emission_temp": 110},
                {"planet_name": "Ganymede", "planetary_radius_km": 2634, "orbit_radius_au": 5.2, "albedo": 0.43, "planet_mass": 1.48e23, "actual_emission_temp": 110},
                {"planet_name": "Callisto", "planetary_radius_km": 2410.3, "orbit_radius_au": 5.2, "albedo": 0.19, "planet_mass": 1.08e23, "actual_emission_temp": 99},
                {"planet_name": "Triton", "planetary_radius_km": 1353.4, "orbit_radius_au": 30.07, "albedo": 0.76, "planet_mass": 2.14e22, "actual_emission_temp": 38},
                {"planet_name": "Ceres", "planetary_radius_km": 473, "orbit_radius_au": 2.77, "albedo": 0.09, "planet_mass": 9.39e20, "actual_emission_temp": 167},
                {"planet_name": "Eris", "planetary_radius_km": 1163, "orbit_radius_au": 67.67, "albedo": 0.96, "planet_mass": 1.67e22, "actual_emission_temp": 30},
                {"planet_name": "Haumea", "planetary_radius_km": 816, "orbit_radius_au": 43.22, "albedo": 0.51, "planet_mass": 4.01e21, "actual_emission_temp": 50},
                {"planet_name": "Makemake", "planetary_radius_km": 715, "orbit_radius_au": 45.79, "albedo": 0.81, "planet_mass": 3.1e21, "actual_emission_temp": 40},
                {"planet_name": "Kepler-22b", "planetary_radius_km": 12050, "orbit_radius_au": 0.85, "albedo": 0.42, "planet_mass": 3.65e25, "actual_emission_temp": 300},
                {"planet_name": "Proxima Centauri b", "planetary_radius_km": 7164, "orbit_radius_au": 0.0485, "albedo": 0.38, "planet_mass": 1.27e25, "actual_emission_temp": 270},
                {"planet_name": "Alpha Centauri Bb", "planetary_radius_km": 6471, "orbit_radius_au": 1.1, "albedo": 0.35, "planet_mass": 4.12e25, "actual_emission_temp": 260},
                {"planet_name": "Gliese 581g", "planetary_radius_km": 7600, "orbit_radius_au": 0.15, "albedo": 0.28, "planet_mass": 3.2e25, "actual_emission_temp": 240},
                {"planet_name": "HD 209458 b", "planetary_radius_km": 15550, "orbit_radius_au": 0.047, "albedo": 0.13, "planet_mass": 2.12e27, "actual_emission_temp": 1200},
                {"planet_name": "TRAPPIST-1d", "planetary_radius_km": 5100, "orbit_radius_au": 0.022, "albedo": 0.23, "planet_mass": 1.04e24, "actual_emission_temp": 290},
                {"planet_name": "TRAPPIST-1e", "planetary_radius_km": 5632, "orbit_radius_au": 0.029, "albedo": 0.32, "planet_mass": 1.26e24, "actual_emission_temp": 270},
                {"planet_name": "TRAPPIST-1f", "planetary_radius_km": 5831, "orbit_radius_au": 0.037, "albedo": 0.36, "planet_mass": 1.34e24, "actual_emission_temp": 250},
                {"planet_name": "TRAPPIST-1g", "planetary_radius_km": 5820, "orbit_radius_au": 0.046, "albedo": 0.29, "planet_mass": 1.37e24, "actual_emission_temp": 230},
                {"planet_name": "Kepler-452b", "planetary_radius_km": 11190, "orbit_radius_au": 1.05, "albedo": 0.40, "planet_mass": 5.23e25, "actual_emission_temp": 290},
                {"planet_name": "Kepler-186f", "planetary_radius_km": 6520, "orbit_radius_au": 0.4, "albedo": 0.37, "planet_mass": 3.26e24, "actual_emission_temp": 265},
                {"planet_name": "GJ 1214b", "planetary_radius_km": 16000, "orbit_radius_au": 0.014, "albedo": 0.20, "planet_mass": 1.15e25, "actual_emission_temp": 555},
                {"planet_name": "LHS 1140b", "planetary_radius_km": 7080, "orbit_radius_au": 0.087, "albedo": 0.22, "planet_mass": 6.98e24, "actual_emission_temp": 230},
                {"planet_name": "Kapteyn b", "planetary_radius_km": 6840, "orbit_radius_au": 0.17, "albedo": 0.28, "planet_mass": 4.84e24, "actual_emission_temp": 200},
                {"planet_name": "WASP-12b", "planetary_radius_km": 19050, "orbit_radius_au": 0.022, "albedo": 0.08, "planet_mass": 1.41e27, "actual_emission_temp": 2500},
                {"planet_name": "Kepler-69c", "planetary_radius_km": 7800, "orbit_radius_au": 1.15, "albedo": 0.34, "planet_mass": 3.75e24, "actual_emission_temp": 270},
                {"planet_name": "TOI 700d", "planetary_radius_km": 6370, "orbit_radius_au": 0.163, "albedo": 0.41, "planet_mass": 2.06e24, "actual_emission_temp": 260},
                {"planet_name": "Kepler-1649c", "planetary_radius_km": 6200, "orbit_radius_au": 0.083, "albedo": 0.33, "planet_mass": 3.16e24, "actual_emission_temp": 260},
                {"planet_name": "K2-18b", "planetary_radius_km": 8750, "orbit_radius_au": 0.15, "albedo": 0.39, "planet_mass": 2.39e25, "actual_emission_temp": 270},
                {"planet_name": "Ross 128 b", "planetary_radius_km": 7100, "orbit_radius_au": 0.049, "albedo": 0.31, "planet_mass": 3.72e24, "actual_emission_temp": 290},
                {"planet_name": "Gliese 876d", "planetary_radius_km": 6400, "orbit_radius_au": 0.02, "albedo": 0.29, "planet_mass": 1.93e25, "actual_emission_temp": 170},
                {"planet_name": "Kepler-37b", "planetary_radius_km": 2400, "orbit_radius_au": 0.1, "albedo": 0.20, "planet_mass": 3.2e23, "actual_emission_temp": 440},
                {"planet_name": "Kepler-16b", "planetary_radius_km": 8650, "orbit_radius_au": 0.7, "albedo": 0.44, "planet_mass": 1.98e25, "actual_emission_temp": 200},
                {"planet_name": "HD 189733b", "planetary_radius_km": 16250, "orbit_radius_au": 0.031, "albedo": 0.31, "planet_mass": 1.14e27, "actual_emission_temp": 1200},
                {"planet_name": "Tau Ceti f", "planetary_radius_km": 7500, "orbit_radius_au": 1.35, "albedo": 0.25, "planet_mass": 5.74e24, "actual_emission_temp": 210}
            ]
        }


        self.custom_constraints = [
            lambda vars, res: vars["albedo"] < 1
        ]

        super(Question27, self).__init__(unique_id, seed, variables)

    @staticmethod
    def jupiter_thermal_balance(
        planetary_radius_km,
        orbit_radius_au,
        albedo,
        actual_emission_temp,
        planet_mass,
        planet_name,
        solar_flux_earth,
        gravitational_constant
    ):
        """
        Calculate the thermal balance of Jupiter.

        Parameters:
            planetary_radius_km (float): Mean planetary radius in kilometers.
            orbit_radius_au (float): Mean radius of orbit around the Sun in AU.
            albedo (float): Planetary albedo.
            actual_emission_temp (float): Observed emission temperature (K).
            planet_mass (float): Mass of the planet (kg).

        Returns:
            tuple: Results for parts (a), (b), and (c).
        """
        # Constants
        AU_TO_M = 1.496e11  # Conversion from AU to meters
        RADIUS_CONVERSION = 1e3  # Conversion from km to meters
        STEFAN_BOLTZMANN_CONSTANT = 5.67e-8  # W/m^2/K^4

        # solar_flux_earth = 1367  # Solar flux at Earth's orbit (W/m^2)
        # gravitational_constant = 6.7e-11  # Gravitational constant (m^3/kg/s^2)

        # Convert planetary radius to meters
        planetary_radius_m = planetary_radius_km * RADIUS_CONVERSION

        # Convert orbit radius to meters
        orbit_radius_m = orbit_radius_au * AU_TO_M

        # (a) Calculate emission temperature
        solar_flux_jupiter = solar_flux_earth / (orbit_radius_au ** 2)
        net_solar_input = (1 - albedo) * solar_flux_jupiter
        emission_temp = ((net_solar_input) / (4 * STEFAN_BOLTZMANN_CONSTANT)) ** 0.25

        # (b) Calculate internal heat source
        net_thermal_emission = 4 * math.pi * (planetary_radius_m ** 2) * STEFAN_BOLTZMANN_CONSTANT * (actual_emission_temp ** 4)
        solar_input = math.pi * (planetary_radius_m ** 2) * net_solar_input
        internal_heat_source = net_thermal_emission - solar_input

        # (c) Calculate radius contraction rate
        radius_contraction_rate = (
            (40 * math.pi / 3) * 
            (planetary_radius_m ** 2) * 
            internal_heat_source / 
            (gravitational_constant * (planet_mass ** 2))
        )

        # Convert contraction rate to meters per year
        seconds_per_year = 365.25 * 24 * 3600
        contraction_rate_per_year = radius_contraction_rate * seconds_per_year

        return NestedAnswer({
            "(a)": Answer(emission_temp, "K", 1),
            "(b)": Answer(internal_heat_source, "W", -10),
            "(c)": Answer(contraction_rate_per_year, "m/yr", 4)
        })


if __name__ == '__main__':
    q = Question27(unique_id="q")
    print(q.question())
    print(q.answer())