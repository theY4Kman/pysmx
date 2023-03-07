import math

from smx.sourcemod.natives.base import native, SourceModNativesMixin


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

    # TODO(zk): random numbers
