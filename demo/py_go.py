
import ctypes

lib = ctypes.CDLL('demo/sum.so')
print(lib.Sum(7, 11))
