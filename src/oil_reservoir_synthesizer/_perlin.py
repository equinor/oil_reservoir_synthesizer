import math

from ._prime_generator import PrimeGenerator


class PerlinNoise:
    def __init__(self, persistence=0.5, number_of_octaves=4, prime_generator=None):
        self.persistence = persistence
        self.number_of_octaves = number_of_octaves

        self.octave_primes = (
            prime_generator if prime_generator is not None else PrimeGenerator()
        )

    def cosine_interppolation(self, a, b, x):
        ft = x * 3.1415927
        f = (1.0 - math.cos(ft)) * 0.5
        return a * (1 - f) + b * f

    MAX_INT = (1 << 31) - 1

    def noise(self, x, perturbation):
        x += perturbation
        x = ((x << 13) & PerlinNoise.MAX_INT) ^ x
        x = (x * (x * x * 15731 + 789221) + 1376312589) & PerlinNoise.MAX_INT
        return 1.0 - x / 1073741824.0

    def smoothed_noise(self, x, perturbation):
        return (
            self.noise(x, perturbation) / 2.0
            + self.noise(x - 1, perturbation) / 4.0
            + self.noise(x + 1, perturbation) / 4.0
        )

    def interpolated_noise(self, x, octave_number):
        int_x = int(x)
        frac_x = x - int_x

        perturbation = self.octave_primes[octave_number]

        v1 = self.smoothed_noise(int_x, perturbation)
        v2 = self.smoothed_noise(int_x + 1, perturbation)

        return self.cosine_interppolation(v1, v2, frac_x)

    def perlin_noise_1d(self, x):
        total = 0.0

        for octave in range(int(self.number_of_octaves) - 1):
            frequency = math.pow(2, octave)
            amplitude = math.pow(self.persistence, octave)

            total += (
                self.interpolated_noise(x * frequency, octave_number=octave) * amplitude
            )

        return total

    def __getitem__(self, x):
        """:rtype: float"""
        return self.perlin_noise_1d(x * 10.0)

    def __call__(self, x):
        """:rtype: float"""
        return self[x]
