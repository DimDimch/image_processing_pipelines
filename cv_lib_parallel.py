import multiprocessing


class CVLibParallel:
    def __init__(self):
        self.pool = multiprocessing.Pool(processes=4)

    def run(self, tasks):
        results = {}

        for task in tasks:
            results[task] = self.pool.apply_async(tasks[task]['func'], tasks[task]['args'])
        return results
