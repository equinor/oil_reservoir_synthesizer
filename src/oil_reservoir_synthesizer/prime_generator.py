import numbers
import random


def rwh_primes2(n):
    # http://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n-in-python/3035188#3035188
    """Input n>=6, Returns a list of primes, 2 <= p < n"""
    correction = n % 6 > 1
    n = {0: n, 1: n - 1, 2: n + 4, 3: n + 3, 4: n + 2, 5: n + 1}[n % 6]
    sieve = [True] * (n // 3)
    sieve[0] = False
    for i in range(int(n**0.5) // 3 + 1):
        if sieve[i]:
            k = 3 * i + 1 | 1
            sieve[((k * k) // 3) :: 2 * k] = [False] * (
                (n // 6 - (k * k) // 6 - 1) // k + 1
            )
            sieve[(k * k + 4 * k - 2 * k * (i & 1)) // 3 :: 2 * k] = [False] * (
                (n // 6 - (k * k + 4 * k - 2 * k * (i & 1)) // 6 - 1) // k + 1
            )
    return [2, 3] + [3 * i + 1 | 1 for i in range(1, n // 3 - correction) if sieve[i]]


class PrimeGenerator:
    LIST_OF_PRIMES = rwh_primes2(10000)

    def __init__(self, seed=None):
        self.__primes = {}
        self.__random = random.Random(seed)
        random.seed(seed)

    def __getitem__(self, index):
        if not isinstance(index, numbers.Rational) or index < 0:
            raise IndexError(f"Index must be a positive integer: {index}")

        if index not in self.__primes:
            p1 = self.randomPrime()
            self.__primes[index] = p1

        return self.__primes[index]

    def randomPrime(self):
        random_index = self.__random.randint(0, len(PrimeGenerator.LIST_OF_PRIMES) - 1)
        return PrimeGenerator.LIST_OF_PRIMES[random_index]
