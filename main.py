from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(pet, plan):
    """Print one pet's generated plan with start times, durations, and priorities."""
    print(f"Today's Schedule for {pet.name} ({pet.species})")
    print("-" * 50)
    for entry in plan.entries:
        hours, minutes = divmod(entry.start_minute, 60)
        task = entry.task
        print(
            f"{hours:02d}:{minutes:02d}  {task.title} "
            f"({task.duration_minutes} min) [{task.priority}]"
        )
    if plan.skipped:
        print("\nSkipped (not enough time):")
        for task in plan.skipped:
            print(f"  - {task.title} ({task.duration_minutes} min)")


def print_pairs(pairs):
    """Print (pet, task) pairs with pet name, preferred time, and status."""
    if not pairs:
        print("  (none)")
    for pet, task in pairs:
        status = "done" if task.completed else "pending"
        print(f"  {task.start_time or '--:--'}  {pet.name}: {task.title} [{status}]")


def main():
    owner = Owner(name="Jordan", available_minutes=120)
    mochi = Pet(name="Mochi", species="dog", owner=owner)
    luna = Pet(name="Luna", species="cat", owner=owner)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks are added out of time order on purpose.
    mochi.add_task(Task("Brush coat", 15, "low", "grooming"))
    mochi.add_task(Task("Evening walk", 30, "high", "walk", start_time="18:00"))

    morning_walk = Task("Morning walk", 30, "high", "walk", start_time="07:30")
    mochi.add_task(morning_walk)
    morning_walk.mark_complete()

    luna.add_task(Task("Feather wand play", 20, "medium", "enrichment", start_time="12:15"))
    luna.add_task(Task("Heart medication", 5, "high", "meds", start_time="08:00"))
    luna.add_task(Task("Catnip time", 10, "low", "enrichment"))  # no time: sorts last

    scheduler = Scheduler(owner)

        # Recurring: completing a daily task creates tomorrow's occurrence.
    mochi.add_task(Task("Give medication", 5, "high", "meds", frequency="daily"))
    mochi.complete_task(mochi.tasks[-1])

    # Conflict: Luna's play overlaps Mochi's walk (07:30-08:00) at 07:45.
    luna.add_task(Task("Laser pointer", 15, "low", "enrichment", start_time="07:45"))

    print("=== All tasks, sorted by time ===")
    all_tasks = [t for pet in owner.pets for t in pet.tasks]
    for task in scheduler.sort_by_time(all_tasks):
        print(f"  {task.start_time or '--:--'}  {task.title}")
    print()

    print("=== Pending tasks ===")
    print_pairs(scheduler.filter_tasks(completed=False))
    print()

    print("=== Completed tasks ===")
    print_pairs(scheduler.filter_tasks(completed=True))
    print()

    print("=== Conflicts ===")
    timed_pairs = scheduler.filter_tasks()
    warnings = scheduler.detect_conflicts(timed_pairs)
    for warning in warnings or ["  (none)"]:
        print(f"  {warning}" if warnings else warning)
    print()

    print("=== Luna's tasks ===")
    print_pairs(scheduler.filter_tasks(pet_name="Luna"))
    print()

    print("=== Generated plans ===")
    for pet in owner.pets:
        print_schedule(pet, scheduler.generate_plan(pet))
        print()


if __name__ == "__main__":
    main()