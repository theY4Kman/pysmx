import ctypes
import math

from smx.definitions import cell
from smx.sourcemod.natives.base import Array, native, SourceModNativesMixin


class FloatNatives(SourceModNativesMixin):
    @native
    def FloatMul(self, a: float, b: float) -> float:
        return a * b

    @native
    def FloatDiv(self, a: float, b: float) -> float:
        return a / b

    @native
    def FloatAdd(self, a: float, b: float) -> float:
        return a + b

    @native
    def FloatSub(self, a: float, b: float) -> float:
        return a - b

    @native
    def FloatFraction(self, value: float) -> float:
        return value % 1.0

    @native
    def RoundToZero(self, value: float) -> float:
        return math.ceil(value) if value < 0 else math.floor(value)

    @native
    def RoundToCeil(self, value: float) -> float:
        return math.ceil(value)

    @native
    def RoundToFloor(self, value: float) -> float:
        return math.floor(value)

    @native
    def RoundToNearest(self, value: float) -> float:
        return round(value)

    @native
    def FloatCompare(self, a: float, b: float) -> int:
        return 1 if a > b else 0 if a == b else -1

    @native
    def SquareRoot(self, value: float) -> float:
        return math.sqrt(value)

    @native
    def Pow(self, base: float, exponent: float) -> float:
        return math.pow(base, exponent)

    @native
    def Exponential(self, value: float) -> float:
        return math.exp(value)

    @native
    def Logarithm(self, value: float, base: float = 10.0) -> float:
        return math.log(value, base)

    @native
    def Sine(self, value: float) -> float:
        return math.sin(value)

    @native
    def Cosine(self, value: float) -> float:
        return math.cos(value)

    @native
    def Tangent(self, value: float) -> float:
        return math.tan(value)

    @native
    def FloatAbs(self, value: float) -> float:
        return math.fabs(value)

    @native
    def ArcTanget(self, value: float) -> float:
        return math.atan(value)

    @native
    def ArcCosine(self, value: float) -> float:
        return math.acos(value)

    @native
    def ArcSine(self, value: float) -> float:
        return math.asin(value)

    @native
    def ArcTangent2(self, y: float, x: float) -> float:
        return math.atan2(y, x)

    @native
    def __FLOAT_GT__(self, a: float, b: float) -> bool:
        return a > b

    @native
    def __FLOAT_GE__(self, a: float, b: float) -> bool:
        return a >= b

    @native
    def __FLOAT_LT__(self, a: float, b: float) -> bool:
        return a < b

    @native
    def __FLOAT_LE__(self, a: float, b: float) -> bool:
        return a <= b

    @native
    def __FLOAT_EQ__(self, a: float, b: float) -> bool:
        return a == b

    @native
    def __FLOAT_NE__(self, a: float, b: float) -> bool:
        return a != b

    @native
    def __FLOAT_NOT__(self, a: float) -> bool:
        return not a

    @native
    def GetURandomInt(self) -> int:
        return self.runtime.rand.randint(0, 0x7FFFFFFF)

    @native
    def GetURandomFloat(self) -> float:
        return self.runtime.rand.random()

    @native
    def SetURandomSeed(self, seeds: Array[int], num_seeds: int) -> None:
        # XXX(zk): can this be done with better DX? casting an Array? built-in Array size?
        seed_bytes = ctypes.cast(seeds.c_ptr, ctypes.POINTER(ctypes.c_byte))
        seed_array = bytearray(seed_bytes[:num_seeds*ctypes.sizeof(cell)])
        self.runtime.rand.seed(seed_array)

    @native
    def float(self, value: int) -> float:
        return float(value)
