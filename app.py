import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# Create the owner once per browser session; reruns reuse the same object.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)
owner = st.session_state.owner

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = st.number_input(
    "Available minutes today", min_value=0, max_value=720, value=owner.available_minutes
)

# --- Adding a pet ---
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

st.table(
    [{"name": p.name, "species": p.species, "tasks": len(p.tasks)} for p in owner.pets]
)
pet_names = [p.name for p in owner.pets]

# --- Scheduling a task ---
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
    task_submitted = st.form_submit_button("Add task")

if task_submitted:
    if not title.strip():
        st.warning("Please enter a task title.")
    else:
        target = next(p for p in owner.pets if p.name == task_pet_name)
        target.add_task(Task(title.strip(), int(duration), priority, category))
        st.success(f"Added '{title.strip()}' to {target.name}.")

# --- Show tasks and generate the plan ---
st.subheader("Tasks and plan")
plan_pet_name = st.selectbox("Plan for", pet_names, key="plan_pet")
plan_pet = next(p for p in owner.pets if p.name == plan_pet_name)

if plan_pet.tasks:
    st.table(
        [
            {
                "title": t.title,
                "minutes": t.duration_minutes,
                "priority": t.priority,
                "category": t.category,
                "done": t.completed,
            }
            for t in plan_pet.tasks
        ]
    )
else:
    st.info(f"{plan_pet.name} has no tasks yet.")

if st.button("Generate schedule"):
    plan = Scheduler(owner).generate_plan(plan_pet)
    if not plan.entries:
        st.warning("No tasks fit the time budget.")
    else:
        st.write(f"**Daily plan for {plan_pet.name}**")
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
    if plan.skipped:
        st.caption("Skipped (not enough time): " + ", ".join(t.title for t in plan.skipped))