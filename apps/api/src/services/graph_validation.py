from __future__ import annotations

from typing import List, Set
from src.services.graph_index import GraphIndex


class GraphViolation:
    def __init__(self, code: str, message: str, extra: dict | None = None):
        self.code = code
        self.message = message
        self.extra = extra or {}

    def dict(self):
        return {
            "code": self.code,
            "message": self.message,
            **({"extra": self.extra} if self.extra else {}),
        }


class GraphValidator:
    """
    Cross-object validation aligned with your modeling rules:
      - All edges connect existing nodes.
      - contributes_to.metricIds must exist on the TARGET node's measurable metrics.
      - (Optional) weights normalization or other rollup preconditions.
    """

    def __init__(self, index: GraphIndex):
        self.idx = index

    def validate(self) -> List[GraphViolation]:
        violations: List[GraphViolation] = []
        violations.extend(self._check_edge_endpoints())
        violations.extend(self._check_contributes_to_metrics())
        return violations

    def _check_edge_endpoints(self) -> List[GraphViolation]:
        out: List[GraphViolation] = []
        ids = self.idx.id_to_node.keys()
        for from_id, edges in self.idx.out_edges_of.items():
            if from_id not in ids:
                out.append(
                    GraphViolation(
                        "UnknownFromNode",
                        f"Edge(s) reference unknown from_node '{from_id}'",
                    )
                )
            for e in edges:
                if e.to_node not in ids:
                    out.append(
                        GraphViolation(
                            "UnknownToNode",
                            f"Edge '{e.edge_id}' references unknown to_node '{e.to_node}'",
                            {"edgeId": e.edge_id},
                        )
                    )
        return out

    def _check_contributes_to_metrics(self) -> List[GraphViolation]:
        out: List[GraphViolation] = []
        for from_id, edges in self.idx.out_edges_of.items():
            for edge in edges:
                if getattr(edge, "kind", None) == "contributes_to":
                    target_metrics: Set[str] = self.idx.metrics_on.get(edge.to_node, set())
                    missing = [
                        m
                        for m in getattr(edge, "metric_ids", [])
                        if m not in target_metrics
                    ]
                    if missing:
                        out.append(
                            GraphViolation(
                                "UnknownTargetMetric",
                                f"Edge '{edge.edge_id}' refers to metricIds not present on target '{edge.to_node}'",
                                {
                                    "edgeId": edge.edge_id,
                                    "missing": missing,
                                    "target": edge.to_node,
                                },
                            )
                        )
        return out
