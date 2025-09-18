from typing import Dict, List, Optional

from schemas.node import NodeUnion
from src.schemas.graph import Graph

class GraphStore:
    def __init__(self):
        self._by_id: Dict[str, Graph] = {}

    def save(self, graph: Graph): self._by_id[graph.graph_id] = graph
    def load(self, graph_id: str) -> Graph: return self._by_id[graph_id]
    def exists(self, graph_id: str) -> bool: return graph_id in self._by_id