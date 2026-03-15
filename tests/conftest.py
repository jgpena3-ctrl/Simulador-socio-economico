import importlib.util
import random
import sys
import types


if importlib.util.find_spec("numpy") is None and "numpy" not in sys.modules:
    rng = random.Random()

    class RandomNS:
        @staticmethod
        def seed(value=None):
            rng.seed(value)

        @staticmethod
        def random():
            return rng.random()

        @staticmethod
        def normal(mu=0.0, sigma=1.0):
            return rng.gauss(mu, sigma)

        @staticmethod
        def randint(low, high=None, size=None):
            if high is None:
                high = low
                low = 0

            def _one():
                return rng.randrange(low, high)

            if size is None:
                return _one()
            return [_one() for _ in range(size)]

        @staticmethod
        def choice(seq, p=None):
            if not seq:
                raise IndexError("Cannot choose from an empty sequence")
            if p is None:
                return seq[rng.randrange(len(seq))]

            total = sum(p)
            threshold = rng.random() * total
            acc = 0.0
            for item, weight in zip(seq, p):
                acc += weight
                if threshold <= acc:
                    return item
            return seq[-1]

    numpy_stub = types.ModuleType("numpy")
    numpy_stub.random = RandomNS()
    numpy_stub.array = lambda values: list(values)
    numpy_stub.array_equal = lambda a, b: list(a) == list(b)

    sys.modules["numpy"] = numpy_stub
