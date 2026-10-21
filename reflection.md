# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My first UML had five classes: `Owner`, `Pet`, `Task`, `Scheduler`, and `DailyPlan`, plus `ScheduledTask` to hold each planned entry with its start time and reason. `Owner` held the name and daily time budget, `Pet` held its tasks, `Task` described one care activity, `Scheduler` built a plan for one pet, and `DailyPlan` held the ordered entries and skipped tasks. I kept the scheduler separate from the data classes so the scheduling rules could change without touching how pets and tasks are stored.

**b. Design changes**

The design changed in several places. The biggest was that `Owner` had no way to hold pets, so I added `pets` and `add_pet()`. Without that, the UI had nowhere to put a new pet. I also added `completed` and `mark_complete()` to `Task` because the first test needed them. Later I added `start_time`, `frequency`, and `due_date` so the scheduler could sort by time, detect conflicts, and handle recurring tasks, and `Pet.complete_task()` so a completed recurring task would create its next occurrence. Finally, `make_pet` in the tests exposed a design risk: a `Pet` that isn't registered with its `Owner` is silently ignored by scheduling and filtering. I haven't fixed that yet. Having `Pet.__post_init__` register itself is the planned fix.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: the owner's daily time budget, each task's priority (high, medium, low), and each task's duration. It also reads optional preferred start times for sorting and conflict detection. Time budget mattered most, because a plan that exceeds it isn't usable. Priority came next, because the owner needs essential care like medication to be planned before enrichment. Preferred start times came last, since the generated plan doesn't use them yet.

**b. Tradeoffs**

`detect_conflicts` flags any two timed tasks whose durations overlap, which catches a 30-minute walk and a 5-minute medication that starts during it. However, `generate_plan` still stacks tasks back to back from 8:00 and ignores `start_time` entirely. So the warnings describe the owner's stated preferences, while the generated plan doesn't follow them. I chose this because respecting every preferred time while also fitting a budget and priorities would need a full scheduling search, which is more complexity than a single-day planner needs. The result is that the warnings are useful for catching clashes in what the owner entered, but the plan itself should be read as a suggested order, not a timetable.

---

## 3. AI Collaboration

**a. How you used AI**

I used an AI assistant to brainstorm the class design, draft the UML diagram, generate Python stubs from it, implement the scheduling methods, draft the first tests, and write these docstrings and docs. The most useful prompts were specific ones that named the design decision I needed to make, such as "one pet at a time" or "durations, not fixed times," because the answers then matched the scenario instead of a generic pet app.

**b. Judgment and verification**

The clearest case of not accepting a suggestion as-is was the test file. The assistant's first test called `mark_complete()`, but my `Task` class had no such method or `completed` field, since I had left them out of the stubs. Running the test would have failed immediately. I added the field and method deliberately, as a small design change, rather than changing the test to match the code. I also decided the tie-breaking rule myself: within a priority level, shorter tasks go first so more of them fit the budget. The assistant had suggested considering both options, and I chose the shorter-first rule because it fits the goal of finishing as many care tasks as possible.

Later, the assistant's code had several bugs that only showed up when I ran it: a self-import at the top of `pawpal_system.py`, a test file in the wrong folder, and three failing tests. The failures came from the test helper, which created pets without registering them with the owner, so the scheduler never saw them. I verified each fix by rerunning `python -m pytest` and `python main.py`. [Add any other bugs you found and how you fixed them.]

---

## 4. Testing and Verification

**a. What you tested**

The suite covers five areas. Sorting checks that timed tasks come back in chronological order and untimed tasks go last. Recurrence checks that daily and weekly tasks create a next occurrence 1 and 7 days later, including across a month boundary, and that one-time tasks create none. Conflict detection checks that exact matches and overlapping durations are flagged, while back-to-back tasks, completed tasks, and untimed tasks are not. Plan generation checks budget limits, priority ordering, and pets with no tasks. Filtering checks completion status and pet name. These tests matter because they cover the rules a pet owner would rely on: nothing gets scheduled past the time budget, urgent care comes first, and recurring care doesn't disappear after one day.

**b. Confidence**

I'm fairly confident in the behaviors the tests cover, since all 22 pass and the tests check specific expected outputs. My confidence is lower for anything outside them. Next I would test: a task whose start time is 23:59 with a duration that runs past midnight, two tasks with identical start times and identical durations, a weekly task that is completed late (whether its next due date should be based on the completion date or the original due date), an owner with zero available minutes, and a recurring task whose start time has no value. I'd also test that `Pet` registration can't be skipped once the auto-registration change is made.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the separation between the data classes and the `Scheduler`. Because `Scheduler` only reads from `Owner`, `Pet`, and `Task`, I could add sorting, filtering, and conflict detection without changing the classes they operate on. The tests also made the pet-registration bug visible right away, which showed the value of writing them.

**b. What you would improve**

I would make `generate_plan` respect preferred start times, so the plan and the conflict warnings agree. I would also register pets automatically in `Pet.__post_init__` so they can't be left out of scheduling. I'd also share one time budget across all pets, instead of giving each pet the owner's full budget.

**c. Key takeaway**

The AI wrote code quickly, but several of its suggestions were wrong in ways that only showed up when I ran the program. Running the code and reading the failure messages was more reliable than trusting the draft. The architect's job is to decide what the system should do, choose the tradeoffs, and verify the result. The assistant can draft the parts, but I need to own the interfaces and the test results.