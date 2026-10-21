# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```
(.venv) (base) srinarendrula@Sris-MacBook-Pro ai110-module2show-pawpal-starter % python main.py
=== All tasks, sorted by time ===
  07:30  Morning walk
  07:45  Laser pointer
  08:00  Heart medication
  12:15  Feather wand play
  18:00  Evening walk
  --:--  Brush coat
  --:--  Give medication
  --:--  Give medication
  --:--  Catnip time

=== Pending tasks ===
  --:--  Mochi: Brush coat [pending]
  18:00  Mochi: Evening walk [pending]
  --:--  Mochi: Give medication [pending]
  12:15  Luna: Feather wand play [pending]
  08:00  Luna: Heart medication [pending]
  --:--  Luna: Catnip time [pending]
  07:45  Luna: Laser pointer [pending]

=== Completed tasks ===
  07:30  Mochi: Morning walk [done]
  --:--  Mochi: Give medication [done]

=== Conflicts ===
  (none)

=== Luna's tasks ===
  12:15  Luna: Feather wand play [pending]
  08:00  Luna: Heart medication [pending]
  --:--  Luna: Catnip time [pending]
  07:45  Luna: Laser pointer [pending]

=== Generated plans ===
Today's Schedule for Mochi (dog)
--------------------------------------------------
08:00  Give medication (5 min) [high]
08:05  Give medication (5 min) [high]
08:10  Evening walk (30 min) [high]
08:40  Morning walk (30 min) [high]
09:10  Brush coat (15 min) [low]

Today's Schedule for Luna (cat)
--------------------------------------------------
08:00  Heart medication (5 min) [high]
08:05  Feather wand play (20 min) [medium]
08:25  Catnip time (10 min) [low]
08:35  Laser pointer (15 min) [low]

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

The tests in `tests/test_pawpal.py` cover:

- **Sorting:** `sort_by_time` returns timed tasks chronologically and places untimed tasks last.
- **Recurrence:** Daily and weekly tasks produce a next occurrence 1 and 7 days later, including across month boundaries. One-time tasks produce none.
- **Conflict detection:** Exact-time matches and overlapping durations produce warnings. Back-to-back tasks, completed tasks, and untimed tasks do not.
- **Plan generation:** Plans stay within the owner's budget, order high priority first, skip tasks that don't fit, and handle pets with no tasks.
- **Filtering:** `filter_tasks` separates pending and completed tasks and filters by pet name.


Sample test output:

```
# Paste your pytest output here
```
(.venv) (base) srinarendrula@Sris-MacBook-Pro ai110-module2show-pawpal-starter % python -m pytest
=========================================== test session starts ===========================================
platform darwin -- Python 3.13.5, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/srinarendrula/Desktop/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 2 items                                                                                         

test_pawpal.py ..                                                                                   [100%]

============================================ 2 passed in 0.06s ============================================
(.venv) (base) srinarendrula@Sris-MacBook-Pro ai110-module2show-pawpal-starter % 

## Smarter Scheduling

| Feature | Method(s) | Behavior |
|---------|-----------|----------|
| Sorting by time | `Scheduler.sort_by_time()` | Orders tasks by `"HH:MM"` start time. Zero-padded strings sort correctly as text. Untimed tasks go last, in their original order. |
| Sorting by priority | `Scheduler._sort_by_priority()` | Used by `generate_plan`. Orders high, then medium, then low, with shorter tasks first within a priority. |
| Filtering | `Scheduler.filter_tasks()` | Returns `(pet, task)` pairs filtered by completion status, pet name, or both. Pass `None` to skip a filter. |
| Conflict detection | `Scheduler.detect_conflicts()` | Returns warning strings for pending, timed tasks whose time ranges overlap, across all pets. Uses durations, not just exact matches. Never raises. |
| Recurring tasks | `Task.mark_complete()`, `Pet.complete_task()` | Completing a daily or weekly task returns a new task due `timedelta(days=1)` or `timedelta(days=7)` later. `Pet.complete_task()` adds it to the pet's list. |

**Known limitation:** `generate_plan` stacks tasks back to back from the day start and ignores `start_time`. Conflict warnings describe the times the owner entered, while the generated plan is a suggested order, not a timetable.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

**Main UI features:**
- Owner name and daily minutes, set at the top of the page.
- Add-a-pet form, with a table of pets and their task counts.
- Add-a-task form with title, duration, priority, category, optional start time, and repeat setting.
- Task table with Show (All, Pending, Completed) and Pet filters. Rows are sorted by time.
- Timing check showing conflict warnings, or a success message when there are none.
- Mark-complete control, which creates the next occurrence for recurring tasks.
- Daily plan for one pet, with the time budget and skipped tasks.

**Example workflow:**
    1. Enter the owner's available minutes.
    2. Add a pet, such as Mochi (dog).
    3. Add tasks, including one with a start time of 07:30 and one at 07:45 for another pet. Set one task to repeat daily.
    4. Check the Timing check section for the overlap warning.
    5. Mark the daily task complete and see its next due date.
    6. Pick a pet under "Plan for" and click Generate schedule.

**Scheduler behaviors shown:**
- Sorting: the task table lists timed tasks in chronological order, with untimed tasks at the bottom.
- Filtering: switching Show or Pet narrows the table without changing the data.
- Conflicts: overlapping pending tasks produce a warning that names both tasks.
- Recurrence: a completed daily task appears again as a new pending task.
- Planning: the daily plan orders by priority and stops at the time budget.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->



## Implementation Summary

PawPal+ builds a daily care plan for one pet at a time, within the owner's available minutes.

- **Owner** holds the name and daily time budget (`available_minutes`).
- **Pet** holds its name, species, owner, and a list of `Task`s.
- **Task** is one care activity with a duration, a priority (high, medium, or low), a category, and a `completed` flag.
- **Scheduler** takes an `Owner` and produces a `DailyPlan` for a pet. It sorts tasks by priority (shorter tasks first within a priority), keeps the ones that fit the remaining budget, and skips the rest. It then stacks the kept tasks from a start time (8:00 by default) and records a reason for each.
- **DailyPlan** holds the scheduled entries and skipped tasks, and renders them as a text summary.

`main.py` runs the scheduler on two pets and prints each schedule. `tests/test_pawpal.py` covers task completion and task addition with pytest.