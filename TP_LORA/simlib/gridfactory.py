import math
from simlib.randomness import Randomness


class GridFactory:
    @staticmethod
    def create_poisson_grid(width, height, num_devices, force_in_range_1_gw=False):
        if not width or not height:
            raise ValueError('width and height cannot be set to be null')
        if force_in_range_1_gw:
            assert width == 2 and height == 2
        predefined_random = Randomness().get_predefined_random()
        devices_grid = []
        for i in range(num_devices):
            coords = (predefined_random.random() * width, predefined_random.random() * height)
            if force_in_range_1_gw:
                while abs(pow(coords[0] - 1, 2) + pow(coords[1] - 1, 2)) > 0.99:
                    coords = (predefined_random.random() * width, predefined_random.random() * height)
            devices_grid.append(coords)
        return devices_grid


if __name__ == '__main__':
    randomness = Randomness(master=True, seed=4)
    grid = GridFactory.create_poisson_grid(2, 2, 200, True)
    print(grid)
