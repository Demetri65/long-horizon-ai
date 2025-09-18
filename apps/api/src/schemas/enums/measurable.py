from enum import Enum

class MetricType(str, Enum):
    qualitative = "qualitative"
    quantitative = "quantitative"