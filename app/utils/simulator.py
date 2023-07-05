import random
import time
import threading

class Simulator:

    def __init__(self):
        pass

    def generate_values(self, num_values=10):
        return [random.randint(20, 30) for _ in range(int(num_values))]