from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(pet, plan):
    """Print one pet's plan with start times, durations, and priorities."""
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


def main():
    owner = Owner(name="Jordan", available_minutes=120)

    mochi = Pet(name="Mochi", species="dog", owner=owner)
    luna = Pet(name="Luna", species="cat", owner=owner)

    mochi.add_task(Task("Morning walk", 30, "high", "walk"))
    mochi.add_task(Task("Breakfast", 10, "high", "feeding"))
    mochi.add_task(Task("Brush coat", 15, "low", "grooming"))

    luna.add_task(Task("Heart medication", 5, "high", "meds"))
    luna.add_task(Task("Feather wand play", 20, "medium", "enrichment"))

    scheduler = Scheduler(owner)
    for pet in (mochi, luna):
        plan = scheduler.generate_plan(pet)
        print_schedule(pet, plan)
        print()


if __name__ == "__main__":
    main()