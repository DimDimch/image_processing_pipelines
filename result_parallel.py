from cvlib import *
from cv_lib_parallel import CVLibParallel
from files_manager import File

def main(parallel_manager: CVLibParallel):
    input_A = File(r'C:\Eyedisks\M1\lam5301-half.tif')



    res = parallel_manager.run({
        'A': {'func': strel3d, 'args': (5, 5, 3, ShapeEnum.DISK, ShapeEnum.SQUARE,)},
        'B': {'func': strel3d, 'args': (11, 11, 5, ShapeEnum.DISK, ShapeEnum.DISK,)},
        'C': {'func': strel, 'args': (9, 9, ShapeEnum.DISK,)},
        'D': {'func': strel3d, 'args': (15, 15, 15, ShapeEnum.DISK, ShapeEnum.DISK,)},
    })
    A = res['A'].get()
    B = res['B'].get()
    C = res['C'].get()
    D = res['D'].get()


    res = parallel_manager.run({
        'E': {'func': vstrel, 'args': (C[1],)},
        'F': {'func': lheq3d, 'args': (input_A + D[1], 1,)},
    })
    E = res['E'].get()
    F = res['F'].get()

    G = despekle3d(F[1], 6)
    H = median3d(G[1] + B[1], 1)
    I = invert3d(H[1])
    J = gerosion3d(I[1] + B[1], 1)
    K = reconstruct3d(I[1] + J[1], Connectivity3dEnum.SIX)
    L = median3d(K[1] + B[1], 1)
    M = invert3d(L[1])
    N = cwtsd3d(M[1], Connectivity3dEnum.TWENTY_SIX)
    O = getp(N[1], 10)
    P = sselect(O[1] + E[1], 10000, 1500, SselectRuleEnum.ACCEPT, 0.0005, ConnectivityEnum.EIGHT)
    Q = rec3dbp(N[1] + P[1], Connectivity3dEnum.SIX, 10)

    res = parallel_manager.run({
        'R': {'func': mul3d, 'args': (L[1] + Q[1],)},
        'S': {'func': gerosion3d, 'args': (Q[1] + A[1], 1,)},
    })
    R = res['R'].get()
    S = res['S'].get()

    T = invert3d(S[1])
    U = mul3d(Q[1] + T[1])
if __name__ == "__main__":
    main(CVLibParallel())
