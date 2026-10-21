import re
from dataclasses import dataclass, field
from datetime import date, timedelta

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
FREQUENCY_DAYS = {"daily": 1, "weekly": 7}
TIME_PATTERN = re.compile(r"([01]\d|2[0-3]):[0-5]\d")


@dataclass
class Owner:
    """A pet owner, their daily time budget, and their pets."""

    name: str
    available_minutes: int
    pets: list["Pet"] = field(default_factory=list, repr=False)

    def __post_init__(self):
        """Reject negative time budgets."""
        if self.available_minutes < 0:
            raise ValueError("available_minutes must be non-negative")

    def add_pet(self, pet: "Pet") -> None:
        """Register a pet under this owner, rejecting duplicate names."""
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"A pet named {pet.name} already exists")
        self.pets.append(pet)


FREQUENCY_DAYS = {"daily": 1, "weekly": 7}


@dataclass
class Task:
    """A single pet care activity."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    category: str  # e.g., "walk", "feeding", "meds", "enrichment", "grooming"
    completed: bool = False
    start_time: str | None = None  # optional preferred time, "HH:MM"
    frequency: str = "once"  # "once", "daily", or "weekly"
    due_date: date | None = None

    def __post_init__(self):
        """Reject invalid durations, priorities, times, and frequencies."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")
        if self.start_time is not None and not TIME_PATTERN.fullmatch(self.start_time):
            raise ValueError("start_time must be HH:MM, e.g. '08:30'")
        if self.frequency not in ("once", "daily", "weekly"):
            raise ValueError("frequency must be 'once', 'daily', or 'weekly'")

    def mark_complete(self) -> "Task | None":
        """Mark this task done and return its next occurrence if it recurs.

        Daily and weekly tasks produce a new Task due one period after this
        task's due_date (or today, if no due_date is set). One-time tasks
        return None. The new task is not completed.
        """
        self.completed = True
        if self.frequency not in FREQUENCY_DAYS:
            return None
        base = self.due_date or date.today()
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            start_time=self.start_time,
            frequency=self.frequency,
            due_date=base + timedelta(days=FREQUENCY_DAYS[self.frequency]),
        )


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
    def complete_task(self, task: Task) -> Task | None:
        """Complete a task and append its next occurrence to this pet, if any.

        Call this instead of task.mark_complete() so recurring tasks are not lost.
        Returns the new task, or None for one-time tasks.
        """
        next_task = task.mark_complete()
        if next_task is not None:
            self.tasks.append(next_task)
        return next_task


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

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by HH:MM start time, with untimed tasks last.

        Zero-padded "HH:MM" strings sort correctly as plain text, so no parsing
        is needed. Untimed tasks map to "99:99", which sorts after any valid time.
        Python's sort is stable, so untimed tasks keep their original order.
        """
        return sorted(tasks, key=lambda t: t.start_time or "99:99")

    def filter_tasks(
        self, completed: bool | None = None, pet_name: str | None = None
    ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs across the owner's pets, optionally filtered.

        Pass None for a filter to leave that field unfiltered. Pairs keep the
        owner's pet order and each pet's task order.
        """
        results = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append((pet, task))
        return results

    def detect_conflicts(self, pairs: list[tuple[Pet, Task]]) -> list[str]:
        """Return a warning for each pair of timed, pending tasks whose time ranges overlap.

        Each task's range runs from its start_time to start_time plus its duration.
        Completed and untimed tasks are ignored. Tasks are sorted by start time,
        so the inner loop can stop as soon as a later task starts after the current
        task ends. Warnings are returned as strings and never raise.
        """
        timed = []
        for pet, task in pairs:
            if task.start_time is None or task.completed:
                continue
            hours, minutes = map(int, task.start_time.split(":"))
            start = hours * 60 + minutes
            timed.append((start, start + task.duration_minutes, pet, task))

        timed.sort(key=lambda item: item[0])
        warnings = []
        for i, (_, end_a, pet_a, task_a) in enumerate(timed):
            for start_b, _, pet_b, task_b in timed[i + 1:]:
                if start_b >= end_a:
                    break
                warnings.append(
                    f"Conflict: {pet_a.name}'s '{task_a.title}' overlaps "
                    f"{pet_b.name}'s '{task_b.title}' at {task_b.start_time}"
                )
        return warnings