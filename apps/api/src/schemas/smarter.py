# apps/api/app/models/smarter.py
from typing import Annotated
from pydantic import Field
from src.schemas.enums import MetricType
from src.config import ModelBase
from .common import MetricId, ISODateTime
from src.schemas.enums import Feasibility, Frequency

class Specific(ModelBase):
    label: str
    statement: str

class Metric(ModelBase):
    metric_id: MetricId
    name: str
    type: MetricType
    value: float | int | str
    target: float | int | str
    unit: str | None = None
    description: str

class Achievable(ModelBase):
    rationale: str
    feasibility: Feasibility
    resources: list[str] = []
    constraints: list[str] = []
    confidence: float = Field(ge=0.0, le=1.0)

class RelevanceScore(ModelBase):
    node_id: int
    explanation: str
    confidence: float = Field(ge=0.0, le=1.0)

class Relevant(ModelBase):
    relevance_to_parent: RelevanceScore | None = None
    relevance_to_root: RelevanceScore

class TimeBound(ModelBase):
    start: ISODateTime
    due: ISODateTime

class EvaluationHistoryEntry(ModelBase):
    date: str
    result: str
    notes: str | None = None

class Evaluation(ModelBase):
    eval_id: int
    criteria: list[str] = []
    metrics: list[MetricId] = []
    frequency: Frequency
    methods: list[str] = Field(default_factory=list)  # "self-assessment" | "peer review" | "automated tracking"
    outcome: Annotated[str, Field(pattern="^(on-track|off-track|exceeded)$")]
    history: list[EvaluationHistoryEntry] = []

class MeasurementUpdate(ModelBase):
    metric_id: MetricId
    new_target: float | int | str | None = None
    new_unit: str | None = None

class TimelineUpdate(ModelBase):
    old_deadline: str
    new_deadline: str

class ResourceUpdate(ModelBase):
    resource_id: str
    change: Annotated[str, Field(pattern="^(increase|decrease|reallocate)$")]
    notes: str | None = None

class ReadjustmentChanges(ModelBase):
    scope: str | None = None
    measurement_updates: list[MeasurementUpdate] = []
    timeline_updates: list[TimelineUpdate] = []
    resource_updates: list[ResourceUpdate] = []

class Readjustment(ModelBase):
    trigger: Annotated[str, Field(pattern="^(evaluation|external_event|resource_change|deadline_shift)$")]
    based_on: list[str] = []
    changes: ReadjustmentChanges
    rationale: str

class SmarterForGoalPayload(ModelBase):
    specific: Specific
    measurable: list[Metric] = []
    achievable: list[Achievable] = []
    relevant: Relevant
    time_bound: TimeBound
    evaluate: list[Evaluation] = []
    readjust: list[Readjustment] = []

class SmarterForMilestonePayload(ModelBase):
    specific: Specific
    # no measurable/timeBound for a zero-time milestone
    achievable: list[Achievable] = []
    relevant: Relevant
    # frequency forced to "milestone" in router/business logic if needed
    evaluate: list[Evaluation] = []
    readjust: list[Readjustment] = []

class SmarterForTaskPayload(ModelBase):
    specific: Specific
    # tasks: no measurable/achievable/evaluate
    relevant: Relevant
    time_bound: TimeBound
    readjust: list[Readjustment] = []

# Wrappers to match your "smarter: {...}" nesting
class SmarterForGoal(ModelBase):
    smarter: SmarterForGoalPayload

class SmarterForMilestone(ModelBase):
    smarter: SmarterForMilestonePayload

class SmarterForTask(ModelBase):
    smarter: SmarterForTaskPayload
