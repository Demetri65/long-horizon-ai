from enum import Enum

class EdgeKind(str, Enum):
    dependency = "dependency"
    contributes_to = "contributes_to"
    relates_to = "relates_to"
    validates = "validates"

class EdgeStatus(str, Enum):
    active = "active"
    proposed = "proposed"
    deprecated = "deprecated"