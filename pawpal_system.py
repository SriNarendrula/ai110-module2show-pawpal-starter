from dataclasses import dataclass, field

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Owner:
    """A pet owner and their daily time budget."""

    name: str
    available_minutes: int

    def __post_init__(self):
        """Reject negative time budgets."""
        if self.available_minutes < 0:
            raise ValueError("available_minutes must be non-negative")


@dataclass
class Task:
    """A single pet care activity."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    category: str  # e.g., "walk", "feeding", "meds", "enrichment", "grooming"
    completed: bool = False

    def __post_init__(self):
        """Reject non-positive durations and unknown priorities."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass
class Pet:
    """A pet belonging to an owner, along with its care tasks."""

    name: str
    species: str
    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a care task to this pet's task list."""
        self.tasks.append(task)


@dataclass
class ScheduledTask:
    """A task placed in the day's plan, with its start time and the reason it was included."""

    task: Task
    start_minute: int  # minutes from the day start, computed by the scheduler
    reason: str


@dataclass
class DailyPlan:
    """The result of scheduling: ordered entries plus any tasks that didn't fit."""

    entries: list[ScheduledTask] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)

    def summary(self) -> str:
        """Return the plan as text with times, durations, and reasons."""
        lines = []
        for entry in self.entries:
            hours, minutes = divmod(entry.start_minute, 60)
            task = entry.task
            lines.append(
                f"{hours:02d}:{minutes:02d}  {task.title} "
                f"({task.duration_minutes} min) [{task.priority}] - {entry.reason}"
            )
        if self.skipped:
            lines.append("Skipped: " + ", ".join(t.title for t in self.skipped))
        return "\n".join(lines)


class Scheduler:
    """Builds a DailyPlan for one pet within the owner's time budget."""

    def __init__(self, owner: Owner, day_start_minute: int = 8 * 60):
        """Store the owner and the minute the day's schedule starts."""
        self.owner = owner
        self.day_start_minute = day_start_minute

    def generate_plan(self, pet: Pet) -> DailyPlan:
        """Build a plan for one pet within the owner's time budget."""
        ordered = self._sort_by_priority(pet.tasks)
        fits, skipped = self._fit_to_budget(ordered)

        plan = DailyPlan(skipped=skipped)
        current_minute = self.day_start_minute
        budget_left = self.owner.available_minutes
        for task in fits:
            budget_left -= task.duration_minutes
            reason = (
                f"{task.priority.capitalize()} priority; "
                f"{budget_left} min of budget left after this"
            )
            plan.entries.append(ScheduledTask(task, current_minute, reason))
            current_minute += task.duration_minutes
        return plan

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority, then by shorter duration."""
        return sorted(
            tasks,
            key=lambda t: (PRIORITY_RANK[t.priority], t.duration_minutes),
        )

    def _fit_to_budget(self, tasks: list[Task]) -> tuple[list[Task], list[Task]]:
        """Keep tasks that fit the remaining time and skip the rest."""
        fits, skipped = [], []
        remaining = self.owner.available_minutes
        for task in tasks:
            if task.duration_minutes <= remaining:
                fits.append(task)
                remaining -= task.duration_minutes
            else:
                skipped.append(task)
        return fits, skipped