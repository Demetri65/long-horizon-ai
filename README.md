# Long‑Horizon AI (research prototype ? Maybe ?)

**Mission.** Help researchers explore whether generative systems can make *long‑term* goals feel manageable by decomposing them into executable, trackable steps—so people can plan, adapt, and finish complex work over weeks or months.

> **One‑liner:** A prototype (on a path to a web app) that turns fuzzy, long‑horizon goals into *directed acyclic graphs (DAGs)* of tasks, applies evaluation loops to *re‑plan*, and gives users a graph view to steer. Built for HCI and AI in mind.

---

## Abstract

People struggle to turn long‑term intentions into consistent progress. Classic **goal‑setting theory** shows that clear, challenging, and feedback‑rich goals improve performance; this project translates that insight into an LLM‑assisted planning and execution loop. The system infers a **Hierarchical Task Analysis (HTA)** from a short goal description, then *maps that structure into a deconstructed graph of goals that abide by SMARTER specification*—**S**pecific, **M**easurable, **A**chievable, **R**elevant, **T**ime‑bound, then **E**valuate and **R**eadjust—so there is a basis for ongoing assessment. Plans are represented as a **Directed Acyclic Graph** and rendered as a **graph view**. The goal is to study 3 operation modes—**non‑agentic**, **hybrid**, and **agentic**—to compare decomposition quality, user burden, and completion dynamics on realistic, multi‑week tasks. ([Stanford Medicine][1])

---

## Why this, why now (HCI framing)

* **Clarity + feedback improves outcomes.** In controlled studies, goal clarity and progress feedback systematically boost persistence and performance—motivating explicit structures and checkpoints here. ([Stanford Medicine][1])
* **Task analysis matters for usability.** HTA models goals → subgoals → operations so designers (and here, LLMs) can see dependencies and failure points; it’s a well‑established technique in human factors and UX. ([Nielsen Norman Group][2])
* **Structured reasoning helps LLMs plan.** **Graph‑of‑Thoughts** encourage exploring multiple paths and revising steps, rather than “straight‑line” answers—useful for long‑horizon decomposition and re‑planning. ([arXiv][3])

---

## Research questions

1. Can an LLM‑assisted pipeline produce **HTA‑quality** decompositions for long‑horizon goals (depth, coverage, ordering)? ([Nielsen Norman Group][2])
2. How do **non‑agentic**, **hybrid (Human-in-the-Loop)**, and **agentic** modes trade off completion rate, human interventions, and time‑to‑milestone? (HITL will be designed in established human‑centered AI guidance.) ([pair.withgoogle.com][5])

---

## Approach (methods & representations)

* **Input → HTA → SMARTER.** The system takes a short free‑text goal, infers an **HTA** (hierarchical breakdown), then converts each node into a **SMARTER** record (with measurable indicators and review cadence). We standardize SMARTER as **Evaluate & Readjust**. ([Nielsen Norman Group][2])
* **Planning as a graph.** Plans are **DAGs** (not just trees): cross‑links capture real dependencies (e.g., “budget approved” gates both “book venue” and “order merch”). We render this as an interactive **graph view**. ([arXiv][6])
* **Thought‑structured prompting.** We adapt **Graph of Thoughts** prompting at plan time and during re‑planning, allowing multiple candidate decompositions, self‑evaluation, and backtracking. ([arXiv][3])
* **Evaluation loops.** On a schedule, the system checks progress against SMARTER metrics and **re‑plans** by updating the DAG: adding/removing nodes, adjusting sequencing, and updating definitions of “done.” ([Lark][4])

---

## Modes of operation

* **Non‑agentic** (initial focus): The system outputs the DAG + SMARTER specs; *the human executes tasks*. Completion is marked by the user in the UI.
* **Hybrid (HITL)**: Semi‑autonomous assistance—e.g., drafting emails or documents—while the human approves/edits critical steps and gates execution. We follow human‑centered AI guidance on review/override patterns. ([pair.withgoogle.com][5])
* **Agentic**: Fully autonomous execution within bounded tools; the **Graph‑of‑Thought** is visible so users can intervene if drift is detected (pause, nudge, or reroute subgraphs). For context on agentic patterns, see **ReAct** and **Voyager** as exemplars of reasoning‑plus‑acting and lifelong skill acquisition. ([arXiv][3])

---

## Example long‑horizon scenarios (used in demos & studies)

1. **Finish a Linear Algebra online course**
   * Decompose into weekly modules, problem‑set cadence, spaced review, and milestone quizzes; track SMARTER metrics like “hours/week” and “quiz pass rate.”
2. **Plan a 10K charity run**
   * Venue permits, sponsor outreach, route design, volunteer staffing, risk checklist, and comms calendar; graph dependencies enforce realistic orderings.
3. **Organize my finances**
   * Aggregate accounts, build a monthly cash‑flow model, debt prioritization plan, and automation checklist; monthly review loop adjusts targets and tasks.

---

## System at a glance

* **Architecture (prototype):** Python back‑end + a Next.js front‑end.
* **Representations:** HTA‑derived **DAG** with node‑level SMARTER fields; visible **graph view** for progress and re‑planning.
* **UX moments:** create goal → inspect/edit DAG → run periodic **Evaluate/Readjust** → mark completions (non‑agentic) or approve drafts (hybrid) → compare deltas between plan versions.

> **Status:** Early research prototype; **non‑agentic** flow ships first. A short demo video exists and is here &#8595;

---

## Evaluation plan

**Metrics (primary).**

* **Task completion rate**, **decomposition depth/quality**, **time‑to‑milestone**, **# of human interventions** (hybrid/agentic).

**Baselines (no‑AI).**

* Human‑written plan baselines, e.g., (a) a flat checklist authored by a basic LLM, and (b) a manual task list created by the participants to achieve a goal.

**Study materials / reproducibility.**

* We will publish task scripts and instructions so others can replicate results; we’ll also reference open research on structured reasoning for context. ([arXiv][3])

---

## Contact

Maintainer: **[@demetri65](https://github.com/demetri65)**
Questions & collaborations: dsl418@nyu.edu | demetri.lopez1599@gmail.com

---

## References (WIP) 

* **Goal‑setting theory.** Locke & Latham’s retrospective on why specific, challenging goals with feedback improve performance—motivates explicit goals + evaluation loops here. ([Stanford Medicine][1])
* **SMARTER (Evaluate, Readjust).** A practical extension of SMART adding an explicit review cycle—our chosen variant for this project. ([Lark][4])
* **Hierarchical Task Analysis (HTA).** Long‑standing HCI method for breaking goals into subgoals/operations; helpful primer from NN/g. ([Nielsen Norman Group][2])
* **Graph of Thoughts (GoT).** Encourages multi‑path exploration and self‑evaluation during reasoning; we borrow the planning mindset for decomposition/re‑planning. ([arXiv][3])
* **Human‑in‑the‑loop design.** People + AI Guidebook on oversight, review, and defining success—informing our hybrid mode gates. ([pair.withgoogle.com][5])
* **Agentic patterns (context).** ReAct (interleaving reasoning and acting) and Voyager (lifelong skill acquisition in open worlds). ([arXiv][6])

[1]: https://med.stanford.edu/content/dam/sm/s-spire/documents/PD.locke-and-latham-retrospective_Paper.pdf?utm_source=chatgpt.com "Building a Practically Useful Theory of Goal Setting and ..."
[2]: https://www.nngroup.com/articles/task-analysis/?utm_source=chatgpt.com "Task Analysis: Support Users in Achieving Their Goals - NN/g"
[3]: https://ojs.aaai.org/index.php/AAAI/article/view/29720 "Graph of Thoughts: Solving Elaborate Problems with Large Language Models"
[4]: https://www.larksuite.com/en_us/topics/productivity-glossary/smarter-goals?utm_source=chatgpt.com "s.m.a.r.t.e.r. Goals: Achieving Success through Strategic ..."
[5]: https://pair.withgoogle.com/guidebook/?utm_source=chatgpt.com "People + AI Guidebook - Home"
[6]: https://arxiv.org/abs/2210.03629?utm_source=chatgpt.com "ReAct: Synergizing Reasoning and Acting in Language ..."