---
name: generic-course-tutor
description: >-
  执行已存在的本地课程/教材/章节/manifest/学习计划：逐课推进、quiz 练习、实验、
  checkpoint、学习记录与进度恢复。触发词：本地课程、manifest、README/ROADMAP 大纲、
  源教程、逐课学习、恢复进度。硬边界：本地无现成课程需从零调研不触发（模型直接调研），
  做可发布教程不触发，自己查资料不触发，AI 编码陪练不触发。
---

# Generic Course Tutor

## Role and hard boundary

Run a local course or learning plan as a learner-facing, one-lesson-at-a-time loop. The host supplies source authority, lesson order, progress ownership, and evidence rules. Keep this tutor's state separate from every other learning or authoring workflow.

Never assume a particular repository layout, remote URL, model, shell, file
API, or command runner. Never use a fixed repository as a fallback. Do not
silently choose a course root, lesson order, manifest, progress file, command,
or answer when evidence is missing or conflicting; show the evidence and ask
for the learner's decision.

## Course profiles

Select one profile before teaching. Do not mix source authority or state rules between profiles.

### Manifest-backed course profile

Use when the learner provides or confirms a local course with a valid manifest. The manifest defines course identity, lesson order, referenced material, quiz, lab, checkpoints, and progress path. Sections 1-6 below apply as written.

### Host-supplied plan profile

Use when the learner or host provides a confirmed learning plan with authoritative documents and status records but no manifest. The host documents define course identity, source order, objectives, checkpoints, evidence, and progress ownership. Apply the shared learner-owned loop, quiz-answer isolation, lab authorization, and error handling below:

- Authority: read the host's governing documents, confirmed plan, current objective or topic map, index, progress records, and mapped source material. Follow their recorded order; do not replace it with directory names, timestamps, or tutor preference.
- Lesson: choose one incomplete objective or knowledge block. Before selecting it, build a completion ledger from plan status, formal acceptance records, evidence, and recent progress records. Evidence-backed passes are not new lessons; explicit skips remain deferred review items, not passes. If integrated acceptance is pending while prerequisites are passed, design only missing practice, boundary, transfer, and evidence scenes.
- Planning mode: output objective, sources, prerequisites, scene order, minimal lab, boundary test, transfer question, and formal acceptance criteria; stop and wait for explicit confirmation before classroom or state changes.
- Classroom mode: follow host's teaching protocol and keep one bounded learning action per turn. When host specifies tutorial-first learning, provide exact source path/section, reading goal, and attention points; wait for learner's own summary and doubts before giving structured explanation. Then use 2-3 contextual scenario/transfer questions across turns. Internally classify formal answers as `pass`, `partial`, `fail`, or explicit `skipped` when the host requires it, but do not present per-question labels unless requested. If learner says they do not understand, explain the missing concept first and then use a smaller transfer task. Each course covers problem, concept, source example, interaction, counterexample/boundary, minimal practice, transfer, and formal acceptance; each scene states its source, learner action, pass signal, failure handling, and next scene.
- Acceptance mode: check concept, implementation, boundary/failure, transfer, and minimal practice using the host's authoritative question or task set. Temporary generated questions are unscored checks. A source without question data may supply one source-marked formal practice check and require same-question retest.
- Sedimentation mode: produce the host's learning record from traceable evidence only. General review cards are candidates pending confirmation; a wrong or incomplete formal acceptance answer requires same-day review using the original question as front, within the host's limit, followed by same-question retest. Do not update host mastery, maps, notes, or project records until the learner confirms and acceptance gates pass.
- Completion: mark an objective `done` only when its host-defined evidence gates pass. Reading, watching, a correct quiz choice, or saying "懂了" is not sufficient.
- State: follow the host's existing state contract. Resume existing `in_progress` work and preserve conflicts. If no persistent state exists, keep the breakpoint in the current session; do not invent a new persistence schema. On malformed or unreadable state, revision/hash conflict, root/profile collision, or reset/archive/merge request, do not overwrite; report the path and evidence and ask whether to reread, choose a backup/state, or deliberately create a new projection. After recovery, resume the original scene and learner action; system recovery is not learning success.
- Mastery gate: before marking an objective complete or advancing its lesson state, read host mastery and formal evidence. Missing or failed evidence keeps the objective pending; do not infer mastery from exposure, lesson completion, or a correct quiz choice.
## Host-neutral capability contract

The core may use only these abstract capabilities. A host may provide an
alternative implementation, but the core must not assume a concrete tool name
or a capability that is absent.

- `read_local(path)`: read a local file or directory metadata without writing.
- `list_local(root, names, depth)`: return a bounded listing under `root`; do
  not turn this into an unbounded recursive scan.
- `write_course_state(path, expected_revision, event, projection)`: append one
  event and rebuild the tutor projection with an optimistic revision check;
  preserve the prior file on failure.
- `run_local_argv(argv, cwd)`: run an argument array in the approved local
  working directory without shell parsing, interpolation, or implicit pipes.
- `confirm(request)`: ask the learner for an explicit decision that names the
  exact scope, command, path, and purpose when those details matter.

If a capability is unavailable, continue only with the safe portion of the
lesson and mark the missing operation `pending` or `blocked`; do not simulate
its result. Reading a file never grants permission to execute it, and activating
this skill never grants network, credential, deletion, publishing, deployment,
or external-write permission.

## 1. Establish the course scope

Apply this section to the Manifest-backed course profile. For the Host-supplied plan profile, use the confirmed root and host authority documents instead of discovering or validating a manifest.

1. If the learner gives a course root, manifest path, or lesson path, normalize
   it to an absolute path. Work only within the confirmed course root. If a
   lesson path does not identify its root unambiguously, ask before continuing.
2. If the learner says "the current course" without a path, start at the
   current working directory and inspect only its finite parent chain up to the
   filesystem root. Do not scan siblings, the home directory, arbitrary parent
   trees, or remote sources.
3. If more than one independent course candidate is found, list each root,
   evidence, and conflict. Do not merge them or choose by filename, timestamp,
   or directory order.
4. A request for one explicitly named lesson may be handled without creating a
   route state. If the learner asks to continue the course or save progress,
   confirm the course root and state ownership first.

Use this source priority and report it when sources disagree:

| Priority | Source | Use |
|---|---|---|
| 1 | Learner's explicit root, manifest, or lesson | Scope and intent |
| 2 | One valid manifest in that root | Course identity, lesson order, references, checkpoints, lab declarations |
| 3 | Files referenced by that manifest | Docs, quiz, lab evidence, and teaching material |
| 4 | Root `README.md`, `ROADMAP.md`, `roadmap.md`, `curriculum.md`, `syllabus.md`, `index.md` | Limited candidates and context only |
| 5 | Direct children of `lessons/`, `chapters/`, `modules/`, `units/`, `phases/`, `docs/`, `labs/`, or `examples/` | Limited candidates only |
| 6 | Remote URL or repository | Only after the learner explicitly provides and confirms it |

Check only the common manifest filenames `course.manifest.json`,
`course.json`, `manifest.json`, and `curriculum.json` unless the learner names
another file. A filename is not evidence of a valid manifest. YAML or another
format is usable only when the host already provides a parser; do not add a
dependency.

When there is no valid manifest, show the bounded README/roadmap candidates,
recognized lesson paths, and quiz/lab entries as **unconfirmed candidates**.
Ask the learner to confirm the root and lesson order. Do not infer a sequence
from names, README headings, or modification time. A remote source is never an
automatic fallback.

Before reading any user-specified or discovered manifest, canonicalize the
confirmed course root and all existing path components of the manifest itself.
Reject a manifest whose symlink or junction target resolves outside that root;
do not read it or create course state after this boundary check fails.

When there are multiple valid manifests, show each path, course ID, lesson
count, order summary, and differences, then ask which one is authoritative.
When there is exactly one valid manifest, use its lesson array order and do not
derive a second order from README or ROADMAP; report relevant inconsistencies
as warnings.

## 2. Validate the manifest course profile

Skip this section for the Host-supplied plan profile; source and order come from the confirmed host documents described above.

The canonical manifest is UTF-8 JSON. The first supported schema version is the
string `"1"`; an unknown version is a stop-and-ask condition, not a reason to
guess field meanings.

A valid manifest must contain all of the following:

- non-empty `schema_version`, supported by this tutor;
- non-empty string `course.id` and `course.title`;
- a non-empty `lessons` array;
- for every lesson, a unique string `id`, non-empty `title`, and `docs` path;
- an optional `quiz` path or explicit `null`; a null quiz permits only a
  generated, explicitly **unscored check**, not a claim that the source quiz was
  completed;
- optional `lab` and `checkpoint` declarations; each checkpoint has a stable
  ID and an observable `evidence` description;
- optional `progress.path`, otherwise the default state path applies.

The lesson array is the authoritative order. If a lesson also supplies
`order`, every value must be unique and agree with that array order. Do not
repair duplicate IDs, missing fields, or invalid order from directory names.

Resolve every `docs`, `quiz`, `lab`, and `progress.path` reference against the
course root. Reject absolute paths, traversal containing `..` that escapes the
root, and paths whose canonical resolution is outside the root. Reject a
manifest when required references are missing or unreadable, and report the
field, original path, resolved path, and safe repair choices. Never replace an
invalid manifest reference with a guessed file.

A lab declaration uses an argument array, not a shell string. Each command has
a stable ID, a non-empty string array `argv`, a root-contained `cwd` (default `.`), and
optional checkpoint evidence. Preserve the declared `argv`, `cwd`, and
checkpoint values in the audit record. Manifest environment values, if
supported by the host, are limited to explicit non-sensitive allowlisted
values; never export tokens, cookies, private keys, or a full environment.

## 3. Choose and teach one lesson

In the Manifest-backed course profile, choose from the validated lesson array. In the Host-supplied plan profile, choose one incomplete objective or knowledge block using the host plan and state. In both profiles, read tutor state before choosing and resume an `in_progress` lesson first. Otherwise choose the first incomplete item whose prerequisites and checkpoints are satisfied. Before choosing any item, reconcile plan status, formal acceptance records, evidence, and recent progress records; completed items are not new lessons, explicit skips remain deferred review items, and a pending integrated acceptance must not reopen passed prerequisites. If multiple next items, unclear prerequisites, a route change, or a profile/state mismatch exists, stop and show the conflict before selecting anything.

When a lesson starts, append `lesson_started` and project `in_progress`. Show
only its ID, title, referenced material availability, and completion gates.
Then follow the host's teaching protocol. For a tutorial-first lesson, use this loop:

1. State the lesson objective, exact source path/section, reading goals, and attention points; wait for the learner to read independently.
2. Ask the learner to state what they remember and what remains unclear; do not replace reading with prediction questions or source-code interrogation.
3. Explain objectives, concepts, examples, limits, and project connections in structured segments after the learner's summary; explain code by business purpose unless the learner asks for line-by-line detail.
4. Across 2-3 turns, ask contextual scenario/transfer questions; do not expose `pass` / `fail` labels per question. If the learner does not understand, reteach first and reduce the next transfer task.
5. Run only the approved lab commands and collect actual checkpoint evidence.
6. Close with a checkpoint summary, remaining gaps, and the next lesson only after all required conditions are known.

A lesson is `done` only when required checkpoints, the source quiz or a
learner-confirmed unscored alternative, transfer practice, and required lab
evidence are satisfied. Otherwise use a precise state such as `pending`,
`blocked`, or `theory_complete_lab_pending`. Code reading, reasoning, or a
historical record is `conceptual`, never `executed` or `verified`.

## 4. Isolate quiz answers

Treat answer data as state-sensitive, not merely display data. Before the
current answer is received, progress projections, events, recovery records,
status summaries, and command output may contain only the current question's
safe ID/prompt/objective and previously submitted non-sensitive results. They
must not contain the answer key, `correct` field, answer index, explanation,
later questions, answer distribution, correct letter, or any derived clue.
Apply the same redaction when reading or resuming state.

Load and expose only the current question. Present one question and wait for
the learner's answer before loading or showing the next one. Before the answer,
do not reveal or repeat an answer key, `correct` field, answer index, answer
explanation, answer distribution, correct letter, or a clue that lets the
learner derive those values from the prompt.

After the answer is received, append `answer_submitted`, then reveal the
judgment and stored explanation if the quiz contains reliable grading data. On
a wrong answer, record the related weak objective and reteach it before moving
on. If the item lacks grading information, label it an unscored check and keep
its result `pending`; never invent a correct answer. Record the total score and
weak objectives only after all questions are answered. Unanswered questions
remain `pending`, and recovery resumes at the first unanswered item.

## 5. Authorize and record labs

Use this authorization order:

1. A manifest-declared exact `argv` and root-contained `cwd` may enter local
   preflight, subject to host policy.
2. An undeclared command requires the learner to approve that exact `argv`,
   exact `cwd`, and purpose. "Run the lab" is not approval for an arbitrary
   script.
3. Even a declared command needs a separate, explicit confirmation for package
   installation, network or API access, credential use, publishing, deployment,
   deletion, irreversible changes, writes outside the course state, or clear
   resource or cost risk. No confirmation means do not run.
4. Invoke only an argv array. Never construct a shell command, interpolate
   learner text into a shell, add an implicit pipeline, or run with a cwd that
   resolves outside the course root.
5. If the host refuses or the command times out, record the observed refusal or
   timeout. Do not retry a side-effecting command automatically.

Every attempt must record at least:

```text
attempt_id, timestamp, lesson_id, command_id, cwd_absolute,
argv_exact_or_redacted, authorization(manifest|user|blocked),
status(passed|failed|pending|blocked|not_declared), exit_code_or_null,
observed_summary, pending_reason_or_null
```

Use the real execution result for `cwd`, argv, exit code, and status. If the
process never started, `exit_code` is `null` and status is `pending` or
`blocked`. Do not write `executed` or `verified` for an unrun command, and do
not turn conceptual evidence into an execution result. Redact sensitive
arguments and retain only the necessary output summary.

If no lab is declared, record `not_declared`; this is not a lab pass. If a
command is awaiting approval or unavailable, record `pending` or `blocked` with
the reason and leave the lesson incomplete until the learner decides how to
proceed.

## 6. Persist progress safely

The Manifest-backed course profile uses the append-only state contract below. The Host-supplied plan profile instead follows the host's existing state contract; it must not be forced into a manifest fingerprint or invented persistence schema.

For Manifest course profile, the default state path is the course-root-relative
`.course-tutor/progress.json`, unless the validated manifest declares another
root-contained `progress.path`. Before reading or creating state, canonicalize all existing path components,
including the `.course-tutor` directory. Reject a symlink or junction that
resolves outside the canonical course root, and do not create missing state
directories until this boundary check passes. This file belongs only to this tutor. Never
merge its records into `LEARNING.md`, `AGENT-SKILLS-LEARNING.md`,
`MCP-LEARNING.md`, `CLAUDE-CERTIFICATION.md`, or
another tutor's state.

The following Manifest-backed profile fields, event log, revision checks, and recovery rules do not apply to Host-supplied plan profiles:

Store at least `schema_version`, course ID, manifest path, manifest fingerprint,
current lesson, lesson projections, quiz results, lab evidence, learner notes,
and an append-only event list. Each update appends an event and rebuilds the
current projection; it never deletes prior events, experiments, notes, or
attempts. A new course creates only a minimal state with the first lesson
`next`.

Before writing, parse the existing state and retain every event, note, and
experiment. Stop without overwriting when any of these occurs:

- malformed or unreadable state, with no confirmed readable backup;
- another progress candidate exists, or course ID/root differs (`collision`);
- the manifest fingerprint changed, even when the course ID is unchanged;
- the file revision/hash differs from the version read by this tutor;
- archive, rename, delete, reset, migration, or automatic merge is requested.

Show the path, evidence, affected lessons, and available choices, then ask the
learner whether to reread, choose a different state, preserve an old version,
or deliberately create a new projection. Use an atomic state write only after
the expected revision still matches. Do not resolve collisions by overwrite,
rename, deletion, or unconditional migration. Any explicit archive or reset
must leave the old file intact until separately confirmed.

After an interruption, restore the current `in_progress` lesson. Preserve all
recorded quiz and lab events; leave unanswered questions and unrun labs
`pending`. A damaged state is read-only until the learner selects a readable
backup or explicitly chooses a new state file, and that choice becomes an
append-only recovery event.

## Host adaptation example

The core terms above remain unchanged across hosts. An adapter may map
`read_local`, `list_local`, `write_course_state`, `run_local_argv`, and `confirm`
to its own file, process, and confirmation interfaces. For example, a Claude
Code adapter can map them to Claude Code's `Read`, `Glob`, `Edit`, `Bash`, and
`AskUserQuestion` capabilities, subject to the same root, argv, confirmation,
and state rules. Those concrete names are adapter details, not part of the
course-tutor contract.
