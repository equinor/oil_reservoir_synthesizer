import math

from ._perlin import PerlinNoise
from ._prime_generator import PrimeGenerator


class Interpolator:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        assert len(x) == len(y)

    def __call__(self, x):
        if x <= self.x[0]:
            y = self.y[0]
        elif x >= self.x[len(self.x) - 1]:
            y = self.y[len(self.x) - 1]
        else:
            y = None
            for i in range(len(self.x) - 1):
                if self.x[i] <= x < self.x[i + 1]:
                    x_diff = self.x[i + 1] - self.x[i]
                    frac_x = (x - self.x[i]) / x_diff
                    y = self.cosine_interpolation(self.y[i], self.y[i + 1], frac_x)
                    break

        return y

    def cosine_interpolation(self, a, b, x):
        ft = x * 3.1415927
        f = (1.0 - math.cos(ft)) * 0.5
        return a * (1 - f) + b * f


class ShapeFunction:
    def __init__(self, x, y, scale=1.0):
        self.scale = scale
        self.interpolator = Interpolator(x, y)

    def __call__(self, x):
        return self.interpolator(x) * self.scale

    def scaled_copy(self, scale=1.0):
        return ShapeFunction(self.interpolator.x, self.interpolator.y, scale)


class ConstantShapeFunction(ShapeFunction):
    def __init__(self, value):
        super().__init__([0.0], [value])


class ShapedNoise:
    def __init__(  # noqa: PLR0913
        self,
        noise_function,
        shape_function,
        divergence_function,
        offset=0.0,
        cutoff=None,
    ):
        self.shape_function = shape_function
        self.divergence_function = divergence_function
        self.noise_function = noise_function
        self.offset = offset
        self.cutoff = cutoff

    def __call__(self, x, scale=1.0):
        scaled_x = x * scale
        result = self.shape_function(scaled_x) + self.noise_function(
            scaled_x
        ) * self.divergence_function(scaled_x)
        result += self.offset
        if self.cutoff is not None:
            result = max(result, self.cutoff)
        return result


class ShapeCreator:
    @staticmethod
    def createshape_function(count=1000, persistence=0.2, octaves=8, seed=1):
        """@rtype: shape_function"""
        prime_generator = PrimeGenerator(seed=seed)
        perlininator = PerlinNoise(
            persistence=persistence,
            number_of_octaves=octaves,
            prime_generator=prime_generator,
        )

        x_values = [x / float(count) for x in range(count)]
        y_values = [perlininator(x) for x in x_values]

        return ShapeFunction(x_values, y_values)

    @staticmethod
    def create_shaped_perlin_function(  # noqa: PLR0913
        divergence_x,
        divergence_y,
        shape_seed=None,
        perlin_seed=None,
        count=1000,
        persistence=0.2,
        octaves=8,
        offset=0.0,
        cutoff=None,
    ):
        """@rtype: ShapedNoise"""
        shape_function = ShapeCreator.createshape_function(
            count, persistence, octaves, shape_seed
        )
        divergence_function = shape_function(divergence_x, divergence_y)
        prime_generator = PrimeGenerator(perlin_seed)
        perlin_noise = PerlinNoise(persistence, octaves, prime_generator)

        return ShapedNoise(
            perlin_noise,
            shape_function,
            divergence_function,
            offset=offset,
            cutoff=cutoff,
        )

    @staticmethod
    def create_noise_function(  # noqa: PLR0913
        shape_function=None,
        divergence_function=None,
        seed=None,
        persistence=0.2,
        octaves=8,
        offset=0.0,
        cutoff=None,
    ):
        """@rtype: ShapedNoise"""
        if shape_function is None:
            shape_function = ConstantShapeFunction(0.0)

        if divergence_function is None:
            divergence_function = ConstantShapeFunction(1.0)

        prime_generator = PrimeGenerator(seed)
        perlin_noise = PerlinNoise(persistence, octaves, prime_generator)

        noise = ShapedNoise(
            perlin_noise,
            shape_function,
            divergence_function,
            offset=offset,
            cutoff=cutoff,
        )
        return noise
