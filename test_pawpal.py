from pawpal_system import Owner, Pet, Task


def make_pet():
    owner = Owner(name="Jordan", available_minutes=120)
    return Pet(name="Mochi", species="dog", owner=owner)


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