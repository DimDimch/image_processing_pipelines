import os


class ParallelCVLib:
    def __init__(self):
        self.result = {}
        with open('test.py', 'r') as file:
            print(file.read())
            print(os.path.basename(__file__))

    def __call__(self, func):
        def new_func(*args, **kwargs):
            result = func(*args, **kwargs)
            return result
        return new_func


