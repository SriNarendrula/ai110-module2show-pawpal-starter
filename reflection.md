# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

- Why is that tradeoff reasonable for this scenario?

`detect_conflicts` flags any two timed tasks whose durations overlap, which catches a 30-minute walk and a 5-minute medication that starts during it. However, `generate_plan` still stacks tasks back to back from 8:00 and ignores `start_time` entirely. So the warnings describe the owner's stated preferences, while the generated plan doesn't follow them. I chose this because respecting every preferred time while also fitting a budget and priorities would need a full scheduling search, which is more complexity than a single-day planner needs. The result is that the warnings are useful for catching clashes in what the owner entered, but the plan itself should be read as a suggested order, not a timetable.

---

## 3. AI Collaboration

**a. How you used AI**

I used an AI assistant to brainstorm the class design, draft the UML diagram, generate Python stubs from it, implement the scheduling methods, draft the first tests, and write these docstrings and docs. The most useful prompts were specific ones that named the design decision I needed to make, such as "one pet at a time" or "durations, not fixed times," because the answers then matched the scenario instead of a generic pet app.

**b. Judgment and verification**

The clearest case of not accepting a suggestion as-is was the test file. The assistant's first test called `mark_complete()`, but my `Task` class had no such method or `completed` field, since I had left them out of the stubs. Running the test would have failed immediately. I added the field and method deliberately, as a small design change, rather than changing the test to match the code. I also decided the tie-breaking rule myself: within a priority level, shorter tasks go first so more of them fit the budget. The assistant had suggested considering both options, and I chose the shorter-first rule because it fits the goal of finishing as many care tasks as possible.

I verified the result by running `python main.py` to check the printed schedule against the expected order by hand, and by running `python -m pytest` on the tests. [Edit this line to describe any bugs you found while running them.]

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
