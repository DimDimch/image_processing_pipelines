from cvlib import *
from files_manager import File, save_file

input_A = File(r'C:\Eyedisks\M1\lam5301-half.tif')


A = strel3d(window_height=5, window_width=5, window_depth=3, shape_xy=ShapeEnum.DISK, shape_yz=ShapeEnum.SQUARE)
B = strel3d(window_height=11, window_width=11, window_depth=5, shape_xy=ShapeEnum.DISK, shape_yz=ShapeEnum.DISK)
C = strel(window_height=9, window_width=9, shape=ShapeEnum.DISK)
D = strel3d(window_height=15, window_width=15, window_depth=15, shape_xy=ShapeEnum.DISK, shape_yz=ShapeEnum.DISK)
E = vstrel(C[1])
F = lheq3d(input_A + D[1], repetitions=1)
G = despekle3d(F[1], iterations=6)
H = median3d(G[1] + B[1], repetitions=1)
I = invert3d(H[1])
J = gerosion3d(I[1] + B[1], repetitions=1)
K = reconstruct3d(I[1] + J[1], connectivity=Connectivity3dEnum.SIX)
L = median3d(K[1] + B[1], repetitions=1)
M = invert3d(L[1])
N = cwtsd3d(M[1], connectivity=Connectivity3dEnum.TWENTY_SIX)
O = getp(N[1], plane=10)
P = sselect(O[1] + E[1], max_segment=10000, min_segment=1500, rule=SselectRuleEnum.ACCEPT, criterion=0.0005, connectivity=ConnectivityEnum.EIGHT)
Q = rec3dbp(N[1] + P[1], connectivity=Connectivity3dEnum.SIX, plane=10)
R = mul3d(L[1] + Q[1])
S = gerosion3d(Q[1] + A[1], repetitions=1)
T = invert3d(S[1])
U = mul3d(Q[1] + T[1])
