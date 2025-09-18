
# Goal Data Types — Python API

## 0) Imports & Conventions

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Literal, Optional, TypedDict, Union, TypeAlias

# ---------- Primitives / Aliases (unchanged semantics) ----------
NodeId: TypeAlias = str            # e.g., "M3"
DateTime: TypeAlias = str          # ISO 8601 string
MetricID: TypeAlias = str          # links to Metric.metricId

# Placeholder for your actual Edge type (left as-is from your codebase)
Edge: TypeAlias = Any
```
---

## 1) Canonical (Readjusted) Types — Final

This is the **final**, kind-aware representation with narrowed fields per `goal`, `milestone`, and `task`.  
It incorporates the "Readjustments to data type" you provided (including `status` on `NodeBase`).

### 1.1 Base Building Blocks (kept as-is)

```python
class Metric(TypedDict):
    metricId: str
    name: str
    type: Literal["quantitative", "qualitative"]
    value: Union[float, int, str]             # number | str
    target: Union[float, int, str]            # number | str
    unit: Optional[str]
    description: str

class Achievable(TypedDict):
    rationale: str                             # Why the goal is realistic
    feasibility: Literal["low", "medium", "high"]
    resources: List[str]                       # Key resources needed
    constraints: List[str]                     # Limitations to watch
    confidence: float                          # 0.0–1.0 confidence level

class RelevanceScore(TypedDict):
    nodeId: int                                # compare to node
    explanation: str
    confidence: float                           # 0–1 model confidence or calibrated reliability

class Revelant(TypedDict):
    relevanceToParent: Optional[RelevanceScore]  # parentId must exist
    relevanceToRoot: RelevanceScore              # always defined, computed via root

class EvaluationHistoryEntry(TypedDict, total=False):
    date: str
    result: str
    notes: str

class Evaluation(TypedDict, total=False):
    evalID: int
    criteria: List[str]
    metrics: List[MetricID]                    # links directly to Measurement objects
    frequency: Literal["daily", "weekly", "monthly", "milestone"]
    methods: List[Literal["self-assessment", "peer review", "automated tracking"]]
    outcome: Literal["on-track", "off-track", "exceeded"]
    history: List[EvaluationHistoryEntry]
    adjust: Optional[Callable[["Evaluation"], None]]  # optional trigger to feed into "Readjust"

class MeasurementUpdate(TypedDict, total=False):
    metricId: str
    newTarget: Union[float, int, str]          # number | str
    newUnit: str

class TimelineUpdate(TypedDict):
    oldDeadline: str
    newDeadline: str

class ResourceUpdate(TypedDict, total=False):
    resourceId: str
    change: Literal["increase", "decrease", "reallocate"]
    notes: str

class ReadjustmentChanges(TypedDict, total=False):
    scope: str                                  # redefine or narrow the goal
    measurementUpdates: List[MeasurementUpdate] # tweak measurement definitions
    timelineUpdates: List[TimelineUpdate]       # adjust deadlines
    resourceUpdates: List[ResourceUpdate]       # update resources/support

class Readjustment(TypedDict):
    trigger: Literal["evaluation", "external_event", "resource_change", "deadline_shift"]
    basedOn: List[str]                           # References to Evaluate outcomes or history entries
    changes: ReadjustmentChanges
    rationale: str                               # Why the adjustment was made
```

### 1.2 Kind-Specific Narrowing (remove irrelevant fields)

```python
# Milestones have no duration ⇒ remove timeBound-related adjustments.
# Evaluation is allowed but forced to the 'milestone' cadence.
class EvaluationForMilestone(TypedDict, total=False):
    evalID: int
    criteria: List[str]
    metrics: List[MetricID]
    frequency: Literal["milestone"]             # forced frequency
    methods: List[Literal["self-assessment", "peer review", "automated tracking"]]
    outcome: Literal["on-track", "off-track", "exceeded"]
    history: List[EvaluationHistoryEntry]
    adjust: Optional[Callable[["EvaluationForMilestone"], None]]

class ReadjustmentChangesForMilestone(TypedDict, total=False):
    scope: str
    measurementUpdates: List[MeasurementUpdate]
    # NOTE: no timelineUpdates (zero-time milestone)
    resourceUpdates: List[ResourceUpdate]

class ReadjustmentForMilestone(TypedDict):
    trigger: Literal["evaluation", "external_event", "resource_change"]  # no 'deadline_shift'
    basedOn: List[str]
    changes: ReadjustmentChangesForMilestone
    rationale: str

# Tasks are binary/actionable ⇒ no Measurable/Achievable/Evaluate.
# Readjustment still allowed (e.g., scope/resource/timeline changes).
class ReadjustmentChangesForTask(TypedDict, total=False):
    scope: str
    # NOTE: no measurementUpdates on tasks
    timelineUpdates: List[TimelineUpdate]
    resourceUpdates: List[ResourceUpdate]

class ReadjustmentForTask(TypedDict):
    trigger: Literal["evaluation", "external_event", "resource_change", "deadline_shift"]
    basedOn: List[str]
    changes: ReadjustmentChangesForTask
    rationale: str
```

### 1.3 SMARTER by Kind

```python
class Specific(TypedDict):
    label: str        # clamped string for graph view
    statement: str    # clear, detailed outcome

class TimeBound(TypedDict):
    start: DateTime
    due: DateTime

class SmarterForGoalPayload(TypedDict):
    specific: Specific
    measurable: List[Metric]
    achievable: List[Achievable]
    relevant: Revelant
    timeBound: TimeBound
    evaluate: List[Evaluation]
    readjust: List[Readjustment]

class SmarterForGoal(TypedDict):
    smarter: SmarterForGoalPayload

class SmarterForMilestonePayload(TypedDict):
    specific: Specific
    # Removed: "measurable" (often implicit/binary) and "timeBound" (zero-time)
    achievable: List[Achievable]
    relevant: Revelant
    evaluate: List[EvaluationForMilestone]
    readjust: List[ReadjustmentForMilestone]

class SmarterForMilestone(TypedDict):
    smarter: SmarterForMilestonePayload

class SmarterForTaskPayload(TypedDict):
    specific: Specific
    # Removed: "measurable", "achievable", "evaluate" (tasks are binary)
    relevant: Revelant
    timeBound: TimeBound
    readjust: List[ReadjustmentForTask]

class SmarterForTask(TypedDict):
    smarter: SmarterForTaskPayload
```

### 1.4 Node (discriminated union) — Final

```python
class NodeBase(TypedDict):
    nodeId: NodeId                 # e.g., "M3"
    title: str                     # clamped
    status: Literal["not-started", "in-progress", "done"]
    parent: Optional[NodeId]       # nodeId or none
    nodes: List["Node"]            # children
    edges: List[Edge]              # left as-is from your codebase

class GoalNode(NodeBase):
    kind: Literal["goal"]
    smarter: SmarterForGoal

class MilestoneNode(NodeBase):
    kind: Literal["milestone"]
    smarter: SmarterForMilestone

class TaskNode(NodeBase):
    kind: Literal["task"]
    smarter: SmarterForTask

Node: TypeAlias = Union[GoalNode, MilestoneNode, TaskNode]
```
### 1.5 Edge (discriminated union) — Final
class EdgeBase(TypedDict, total=False):
    edgeId: str                         # unique id for this edge
    fromNode: NodeId                    # source node id
    toNode: NodeId                      # target node id
    kind: Literal["dependency", "contributes_to", "relates_to", "validates"]
    label: str                          # short clamped label for graph rendering
    status: Literal["active", "proposed", "deprecated"]
    createdAt: DateTime
    updatedAt: DateTime
    metadata: dict[str, Any]            # free-form bag for adapters/plugins

#### ------------- Dependency (scheduling) -------------
class DependencyEdge(EdgeBase, total=False):
    kind: Literal["dependency"]
    # Project-management style constraints (source -> target)
    # FS: finish-to-start (default), SS: start-to-start, FF: finish-to-finish, SF: start-to-finish
    constraint: Literal["FS", "SS", "FF", "SF"]
    lagHours: int                       # positive, zero, or negative (lead) lag in hours
    hard: bool                          # True = hard constraint, False = soft/preferred
    # Optional scheduling window on the target side
    earliestStart: Optional[DateTime]
    latestFinish: Optional[DateTime]

#### ------------- Contribution (rollups/metrics) -------------
class ContributesToEdge(EdgeBase, total=False):
    kind: Literal["contributes_to"]
    weight: float                       # 0.0–1.0 (how much this source contributes)
    # Which metrics on the TARGET node this edge contributes to (use target-side metrics by default)
    metricIds: List[MetricID]
    # Aggregation strategy when multiple inbound contributions exist
    aggregation: Literal["weighted_sum", "avg", "min", "max", "boolean_or"]

#### ------------- Relatedness (cross-reference) -------------
class RelatesToEdge(EdgeBase, total=False):
    kind: Literal["relates_to"]
    tags: List[str]                     # e.g., ["risk", "similar", "docs"]
    rationale: Optional[str]            # short explanation / link reason

#### ------------- Validation (milestones validating goals) -------------
class ValidatesEdge(EdgeBase, total=False):
    kind: Literal["validates"]
    # Optional link to evaluation artifacts used for validation
    basedOnEvalIds: List[int]           # evalID values from the relevant node(s)
    criteria: List[str]                 # succinct checklist used to validate
    passed: Optional[bool]              # last known validation result (null until checked)

#### ------------- Union -------------
Edge: TypeAlias = Union[DependencyEdge, ContributesToEdge, RelatesToEdge, ValidatesEdge]
```

---

## Semantics & Best Practices

### Directionality
- All edges are **directed** (`fromNode` → `toNode`).
- Store **outgoing** edges in `Node.edges` to avoid duplication. A graph indexer can compute inbound edges when needed.

### Where do edges connect?
- `dependency`: any combination of `task`, `milestone`, or `goal` nodes.
- `contributes_to`: typically `task → goal` or `task → milestone` (roll up to **target-side** metrics listed in `metricIds`).
- `relates_to`: unrestricted; use for navigation and knowledge links.
- `validates`: commonly `milestone → goal` (the milestone *validates* a stated goal outcome).

### Scheduling (dependency)
- Default `constraint` is **FS** (finish-to-start). Use `lagHours` for offsets (negative = lead).
- `hard=True` means the schedule **must** respect the constraint; `hard=False` is a soft preference.
- Optional `earliestStart` / `latestFinish` let you encode guard-rails **on the target node**.

### Rollups (contributes_to)
- `weight` is a normalization hint for progress rollup (keep sum of inbound weights ≤ 1 for simplicity).
- `metricIds` **refer to metrics on the `toNode`** unless you explicitly choose another convention.
- `aggregation` defines how multiple inbound contributions are combined for each metric.

### Validation (validates)
- Link milestone checks to higher-level goals.
- Use `criteria` as a short checklist; tie back to `Evaluation` records via `basedOnEvalIds` if you keep global/unique evaluation IDs.
- `passed` caches the last validation outcome for fast rendering.

### Status & lifecycle
- `status`: `active` (in use), `proposed` (draft), `deprecated` (kept for audit but not used for planning/rollups).
- Keep `createdAt`/`updatedAt` for audit trails and deterministic diffing.

---

## Invariants

- `fromNode` and `toNode` **must** resolve to existing `NodeId`s.
- When an edge is stored inside a node, `edge.fromNode == node.nodeId`.
- For `contributes_to`, each `metricId` **must** exist on the **target** node’s `measurable` list (if the target is a `goal`).  
  Tasks do not carry metrics in your design; point to the goal’s metrics instead.
- `weight` ∈ [0, 1]; if multiple inbound edges contribute to the same metric, system should support normalization or validation.

---

## Examples

### 1) Task A blocks Task B (2‑day lag)
```json
{
  "edgeId": "E-100",
  "fromNode": "TASK-A",
  "toNode": "TASK-B",
  "kind": "dependency",
  "constraint": "FS",
  "lagHours": 48,
  "hard": true,
  "label": "A → B",
  "status": "active"
}
```

### 2) Task C contributes 30% to Goal G’s metrics M1 and M2
```json
{
  "edgeId": "E-200",
  "fromNode": "TASK-C",
  "toNode": "GOAL-G",
  "kind": "contributes_to",
  "weight": 0.3,
  "metricIds": ["M1", "M2"],
  "aggregation": "weighted_sum",
  "label": "C → G (30%)",
  "status": "active"
}
```

### 3) Milestone M validates Goal G based on evaluation record 42
```json
{
  "edgeId": "E-300",
  "fromNode": "MILESTONE-M",
  "toNode": "GOAL-G",
  "kind": "validates",
  "basedOnEvalIds": [42],
  "criteria": ["Spec signed", "QA sign-off"],
  "passed": true,
  "label": "M validates G",
  "status": "active"
}
```

### 4) Goal X relates to Goal Y for context
```json
{
  "edgeId": "E-400",
  "fromNode": "GOAL-X",
  "toNode": "GOAL-Y",
  "kind": "relates_to",
  "tags": ["context", "roadmap"],
  "rationale": "Shared customer outcome theme",
  "status": "proposed"
}
```


---

## 2) Initial Discriminated Union (as first listed)

```python
class NodeBase(TypedDict):
    nodeId: NodeId                 # e.g., "M3"
    title: str                     # clamped
    parent: Optional[NodeId]       # nodeId or none
    nodes: List["Node"]            # children
    edges: List[Edge]              # left as-is from your codebase

class GoalNode(NodeBase):
    kind: Literal["goal"]
    smarter: SmarterForGoal

class MilestoneNode(NodeBase):
    kind: Literal["milestone"]
    smarter: SmarterForMilestone

class TaskNode(NodeBase):
    kind: Literal["task"]
    smarter: SmarterForTask

Node: TypeAlias = Union[GoalNode, MilestoneNode, TaskNode]
```
