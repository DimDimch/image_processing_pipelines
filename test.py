import time

import result
import result_parallel
from cv_lib_parallel import CVLibParallel

n = 5


def main():
    # mean = []
    # for i in range(n):
    #     start_time = time.time()
    #     result.main()
    #     mean.append(time.time() - start_time)
    # print(f"result - {mean}")

    # mean = 0
    # for i in range(n):
    #     start_time = time.time()
    #     result_parallel.main(CVLibParallel())
    #     mean += time.time() - start_time
    # print(f"result_parallel - {mean / n}")

    # start_time = time.time()
    # # result.main()
    # result_parallel.main(CVLibParallel())
    # print(f"result_parallel - {time.time() - start_time}")


if __name__ == "__main__":
    main()
