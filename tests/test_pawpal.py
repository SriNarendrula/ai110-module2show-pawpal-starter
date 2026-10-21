from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler


def make_owner(minutes=120):
    return Owner(name="Jordan", available_minutes=minutes)


def make_pet(owner=None, name="Mochi", species="dog"):
    """Create a pet and register it with the owner so filter_tasks can see it."""
    owner = owner or make_owner()
    pet = Pet(name=name, species=species, owner=owner)
    owner.add_pet(pet)
    return pet


# --- Basic behavior (from the earlier quick tests) ---

def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high", "walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_task_count():
    pet = make_pet()
    before = len(pet.tasks)
    pet.add_task(Task("Breakfast", 10, "high", "feeding"))
    assert len(pet.tasks) == before + 1


# --- Sorting ---

def test_sort_by_time_returns_chronological_order():
    scheduler = Scheduler(make_owner())
    tasks = [
        Task("Dinner", 10, "high", "feeding", start_time="18:00"),
        Task("Breakfast", 10, "high", "feeding", start_time="08:00"),
        Task("Walk", 30, "high", "walk", start_time="07:30"),
    ]
    ordered = scheduler.sort_by_time(tasks)
    assert [t.title for t in ordered] == ["Walk", "Breakfast", "Dinner"]


def test_sort_by_time_puts_untimed_tasks_last():
    scheduler = Scheduler(make_owner())
    tasks = [
        Task("Brush", 15, "low", "grooming"),
        Task("Walk", 30, "high", "walk", start_time="07:30"),
    ]
    ordered = scheduler.sort_by_time(tasks)
    assert [t.title for t in ordered] == ["Walk", "Brush"]


def test_sort_by_time_handles_empty_list():
    assert Scheduler(make_owner()).sort_by_time([]) == []


# --- Recurrence ---

def test_daily_task_creates_next_day_occurrence():
    task = Task("Medication", 5, "high", "meds", frequency="daily", due_date=date(2026, 3, 10))
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == date(2026, 3, 11)
    assert next_task.completed is False


def test_weekly_task_creates_occurrence_seven_days_later():
    task = Task("Bath", 30, "low", "grooming", frequency="weekly", due_date=date(2026, 3, 10))
    assert task.mark_complete().due_date == date(2026, 3, 17)


def test_daily_recurrence_crosses_month_boundary():
    task = Task("Medication", 5, "high", "meds", frequency="daily", due_date=date(2026, 1, 31))
    assert task.mark_complete().due_date == date(2026, 2, 1)


def test_one_time_task_creates_no_next_occurrence():
    task = Task("Vet visit", 60, "high", "meds")
    assert task.mark_complete() is None


def test_pet_complete_task_appends_next_occurrence():
    pet = make_pet()
    task = Task("Medication", 5, "high", "meds", frequency="daily", due_date=date(2026, 3, 10))
    pet.add_task(task)

    pet.complete_task(task)

    assert len(pet.tasks) == 2
    assert pet.tasks[1].due_date == date(2026, 3, 11)


# --- Conflict detection ---

def test_conflict_detected_for_exact_same_start_time():
    owner = make_owner()
    scheduler = Scheduler(owner)
    mochi = make_pet(owner)
    luna = make_pet(owner, name="Luna", species="cat")
    mochi.add_task(Task("Walk", 30, "high", "walk", start_time="09:00"))
    luna.add_task(Task("Play", 10, "low", "enrichment", start_time="09:00"))

    warnings = scheduler.detect_conflicts(scheduler.filter_tasks())

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Play" in warnings[0]


def test_conflict_detected_for_overlapping_durations():
    owner = make_owner()
    scheduler = Scheduler(owner)
    mochi = make_pet(owner)
    mochi.add_task(Task("Walk", 30, "high", "walk", start_time="07:30"))
    mochi.add_task(Task("Medication", 5, "high", "meds", start_time="07:45"))

    assert len(scheduler.detect_conflicts(scheduler.filter_tasks())) == 1


def test_back_to_back_tasks_do_not_conflict():
    owner = make_owner()
    scheduler = Scheduler(owner)
    mochi = make_pet(owner)
    mochi.add_task(Task("Walk", 30, "high", "walk", start_time="07:30"))
    mochi.add_task(Task("Breakfast", 10, "high", "feeding", start_time="08:00"))

    assert scheduler.detect_conflicts(scheduler.filter_tasks()) == []


def test_completed_tasks_are_ignored_in_conflicts():
    owner = make_owner()
    scheduler = Scheduler(owner)
    mochi = make_pet(owner)
    done = Task("Walk", 30, "high", "walk", start_time="09:00", completed=True)
    mochi.add_task(done)
    mochi.add_task(Task("Play", 10, "low", "enrichment", start_time="09:00"))

    assert scheduler.detect_conflicts(scheduler.filter_tasks()) == []


def test_untimed_tasks_are_ignored_in_conflicts():
    owner = make_owner()
    scheduler = Scheduler(owner)
    mochi = make_pet(owner)
    mochi.add_task(Task("Brush", 15, "low", "grooming"))
    mochi.add_task(Task("Walk", 30, "high", "walk", start_time="09:00"))

    assert scheduler.detect_conflicts(scheduler.filter_tasks()) == []


# --- Plan generation ---

def test_plan_respects_budget_and_skips_what_does_not_fit():
    owner = make_owner(minutes=60)
    pet = make_pet(owner)
    pet.add_task(Task("Walk", 30, "high", "walk"))
    pet.add_task(Task("Long grooming", 40, "high", "grooming"))
    pet.add_task(Task("Play", 20, "low", "enrichment"))

    plan = Scheduler(owner).generate_plan(pet)

    assert [e.task.title for e in plan.entries] == ["Walk", "Play"]
    assert [t.title for t in plan.skipped] == ["Long grooming"]
    assert sum(e.task.duration_minutes for e in plan.entries) <= 60


def test_plan_orders_high_priority_first():
    owner = make_owner()
    pet = make_pet(owner)
    pet.add_task(Task("Play", 10, "low", "enrichment"))
    pet.add_task(Task("Medication", 5, "high", "meds"))

    plan = Scheduler(owner).generate_plan(pet)

    assert [e.task.title for e in plan.entries] == ["Medication", "Play"]


def test_plan_for_pet_with_no_tasks_is_empty():
    owner = make_owner()
    plan = Scheduler(owner).generate_plan(make_pet(owner))
    assert plan.entries == []
    assert plan.skipped == []


def test_plan_start_times_stack_from_day_start():
    owner = make_owner()
    pet = make_pet(owner)
    pet.add_task(Task("Walk", 30, "high", "walk"))
    pet.add_task(Task("Breakfast", 10, "high", "feeding"))

    plan = Scheduler(owner, day_start_minute=8 * 60).generate_plan(pet)

    assert plan.entries[0].start_minute == 480
    assert plan.entries[1].start_minute == 480 + plan.entries[0].task.duration_minutes


# --- Filtering ---

def test_filter_by_completion_status():
    owner = make_owner()
    pet = make_pet(owner)
    pet.add_task(Task("Walk", 30, "high", "walk", completed=True))
    pet.add_task(Task("Play", 10, "low", "enrichment"))
    scheduler = Scheduler(owner)

    pending = scheduler.filter_tasks(completed=False)
    done = scheduler.filter_tasks(completed=True)

    assert [t.title for _, t in pending] == ["Play"]
    assert [t.title for _, t in done] == ["Walk"]


def test_filter_by_pet_name():
    owner = make_owner()
    mochi = make_pet(owner)
    luna = make_pet(owner, name="Luna", species="cat")
    mochi.add_task(Task("Walk", 30, "high", "walk"))
    luna.add_task(Task("Play", 10, "low", "enrichment"))

    result = Scheduler(owner).filter_tasks(pet_name="Luna")

    assert [(p.name, t.title) for p, t in result] == [("Luna", "Play")]


def test_filter_with_no_matches_returns_empty_list():
    owner = make_owner()
    assert Scheduler(owner).filter_tasks(pet_name="Ghost") == []