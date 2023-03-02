import math

from smx.sourcemod.natives.base import native, SourceModNativesMixin


class FloatNatives(SourceModNativesMixin):
    @native('float', 'float')
    def FloatMul(self, a: float, b: float) -> float:
        return a * b

    @native('float', 'float')
    def FloatDiv(self, a: float, b: float) -> float:
        return a / b

    @native('float', 'float')
    def FloatAdd(self, a: float, b: float) -> float:
        return a + b

    @native('float', 'float')
    def FloatSub(self, a: float, b: float) -> float:
        return a - b

    @native('float')
    def FloatFraction(self, value: float) -> float:
        return value % 1.0

    @native('float')
    def RoundToZero(self, value: float) -> float:
        return math.ceil(value) if value < 0 else math.floor(value)

    @native('float')
    def RoundToCeil(self, value: float) -> float:
        return math.ceil(value)

    @native('float')
    def RoundToFloor(self, value: float) -> float:
        return math.floor(value)

    @native('float')
    def RoundToNearest(self, value: float) -> float:
        return round(value)

    @native('float')
    def FloatCompare(self, a: float, b: float) -> int:
        return 1 if a > b else 0 if a == b else -1

    @native('float')
    def SquareRoot(self, value: float) -> float:
        return math.sqrt(value)

    @native('float', 'float')
    def Pow(self, base: float, exponent: float) -> float:
        return math.pow(base, exponent)

    @native('float')
    def Exponential(self, value: float) -> float:
        return math.exp(value)

    @native('float', 'float')
    def Logarithm(self, value: float, base: float = 10.0) -> float:
        return math.log(value, base)

    @native('float')
    def Sine(self, value: float) -> float:
        return math.sin(value)

    @native('float')
    def Cosine(self, value: float) -> float:
        return math.cos(value)

    @native('float')
    def Tangent(self, value: float) -> float:
        return math.tan(value)

    @native('float')
    def FloatAbs(self, value: float) -> float:
        return math.fabs(value)

    @native('float')
    def ArcTanget(self, value: float) -> float:
        return math.atan(value)

    @native('float')
    def ArcCosine(self, value: float) -> float:
        return math.acos(value)

    @native('float')
    def ArcSine(self, value: float) -> float:
        return math.asin(value)

    @native('float', 'float')
    def ArcTangent2(self, y: float, x: float) -> float:
        return math.atan2(y, x)

    # TODO(zk): random numbers
