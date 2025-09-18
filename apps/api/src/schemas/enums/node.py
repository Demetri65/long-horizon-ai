from enum import Enum

class NodeKind(str, Enum):
    goal = "goal"
    milestone = "milestone"
    task = "task"

class NodeStatus(str, Enum):
    not_started = "not-started"
    in_progress = "in-progress"
    done = "done"