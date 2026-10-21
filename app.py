import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# The owner lives in session state so it survives Streamlit's reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)
owner = st.session_state.owner
scheduler = Scheduler(owner)

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = st.number_input(
    "Available minutes today", min_value=0, max_value=720, value=owner.available_minutes
)

# --- Add a pet ---
st.subheader("Add a pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_submitted = st.form_submit_button("Add pet")

if pet_submitted:
    if not pet_name.strip():
        st.warning("Please enter a pet name.")
    else:
        try:
            owner.add_pet(Pet(name=pet_name.strip(), species=species, owner=owner))
            st.success(f"Added {pet_name.strip()}.")
        except ValueError as err:
            st.warning(str(err))

if not owner.pets:
    st.info("No pets yet. Add one above.")
    st.stop()

pet_names = [p.name for p in owner.pets]
st.table([{"name": p.name, "species": p.species, "tasks": len(p.tasks)} for p in owner.pets])

# --- Add a task ---
st.subheader("Add a task")
with st.form("add_task_form", clear_on_submit=True):
    task_pet_name = st.selectbox("Pet", pet_names)
    title = st.text_input("Task title", value="Morning walk")
    col1, col2, col3 = st.columns(3)
    with col1:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col2:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col3:
        category = st.selectbox(
            "Category", ["walk", "feeding", "meds", "enrichment", "grooming", "other"]
        )
    col4, col5 = st.columns(2)
    with col4:
        start_time = st.text_input("Start time (optional)", placeholder="HH:MM, e.g. 08:30")
    with col5:
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
    task_submitted = st.form_submit_button("Add task")

if task_submitted:
    if not title.strip():
        st.warning("Please enter a task title.")
    else:
        target = next(p for p in owner.pets if p.name == task_pet_name)
        try:
            target.add_task(
                Task(
                    title=title.strip(),
                    duration_minutes=int(duration),
                    priority=priority,
                    category=category,
                    start_time=start_time.strip() or None,
                    frequency=frequency,
                )
            )
            st.success(f"Added '{title.strip()}' to {target.name}.")
        except ValueError as err:
            st.warning(str(err))

# --- Tasks: filtered and sorted by the Scheduler ---
st.subheader("Tasks")
col_a, col_b = st.columns(2)
with col_a:
    status_choice = st.selectbox("Show", ["All", "Pending", "Completed"])
with col_b:
    pet_choice = st.selectbox("Pet", ["All pets"] + pet_names, key="filter_pet")

completed_filter = {"All": None, "Pending": False, "Completed": True}[status_choice]
pet_filter = None if pet_choice == "All pets" else pet_choice
pairs = scheduler.filter_tasks(completed=completed_filter, pet_name=pet_filter)

if pairs:
    owner_of = {id(task): pet.name for pet, task in pairs}
    ordered = scheduler.sort_by_time([task for _, task in pairs])
    st.table(
        [
            {
                "time": t.start_time or "--:--",
                "task": t.title,
                "pet": owner_of[id(t)],
                "minutes": t.duration_minutes,
                "priority": t.priority,
                "repeats": t.frequency,
                "status": "done" if t.completed else "pending",
            }
            for t in ordered
        ]
    )
else:
    st.info("No tasks match this filter.")

# --- Conflicts: warnings, not errors ---
st.subheader("Timing check")
warnings = scheduler.detect_conflicts(scheduler.filter_tasks())
if warnings:
    for warning in warnings:
        st.warning(
            f"{warning}. Move one of these tasks to another start time, "
            "or shorten it, so the owner can do both."
        )
else:
    st.success("No timing conflicts among pending tasks.")

# --- Mark a task complete (recurring tasks create their next occurrence) ---
pending = scheduler.filter_tasks(completed=False)
if pending:
    st.subheader("Mark a task complete")
    options = {
        f"{pet.name}: {task.title} ({task.start_time or 'no time'})": (pet, task)
        for pet, task in pending
    }
    choice = st.selectbox("Pending task", list(options))
    if st.button("Mark complete"):
        pet, task = options[choice]
        next_task = pet.complete_task(task)
        if next_task is None:
            st.success(f"Completed '{task.title}'.")
        else:
            st.success(
                f"Completed '{task.title}'. Next due {next_task.due_date.isoformat()}."
            )

# --- Daily plan ---
st.subheader("Daily plan")
plan_pet_name = st.selectbox("Plan for", pet_names, key="plan_pet")
plan_pet = next(p for p in owner.pets if p.name == plan_pet_name)

if st.button("Generate schedule"):
    plan = scheduler.generate_plan(plan_pet)
    if plan.entries:
        st.success(
            f"Planned {len(plan.entries)} task(s) for {plan_pet.name} "
            f"within {owner.available_minutes} minutes."
        )
        st.table(
            [
                {
                    "time": f"{e.start_minute // 60:02d}:{e.start_minute % 60:02d}",
                    "task": e.task.title,
                    "minutes": e.task.duration_minutes,
                    "priority": e.task.priority,
                    "why": e.reason,
                }
                for e in plan.entries
            ]
        )
        st.caption(
            "Plan times stack from 08:00 in priority order. They are a suggested "
            "order, not the preferred start times shown above."
        )
    else:
        st.warning("No tasks fit the time budget.")
    if plan.skipped:
        st.info("Skipped (not enough time): " + ", ".join(t.title for t in plan.skipped))