# CLAUDE.md: course repo rules

This is the public student repo for **Cloud Computing and Data Architectures**, SRH University Hamburg, winter 2026. Lecturer: Shyam Savania. Read this before changing anything.

## How this repo is maintained
- This repo is the single source of truth. Claude Code is the only tool that writes to it.
- Planning and slide drafting happen elsewhere (Claude chat). Changes arrive as a written brief. Apply the brief to the files as they are now; don't overwrite newer work with older copies.
- Work on a branch, open a pull request, and let Shyam merge. Never push to main.
- When a brief conflicts with this file, stop and ask.

## Never commit
- Answers, solutions or expected results (instructor material lives outside the repo).
- The evolution brief, the mid-module twist, or the failure test before they're released in class.
- Marking moderation details, emails with SRH staff, or personal contact details.
- Terraform state, `terraform.tfvars`, service account keys, generated data (`data/`, `freight-data/`, `events.jsonl`).

## Module facts
- 15 sessions, 16 Nov to 18 Dec 2026, 16:30-19:00, seminar room 1.4. 21 students.
- Session shape: recap, concepts, industry context, break, workshop (about 80 min; session 1 runs 55).
- Platform: Google Cloud, region `europe-west3`. Databricks Free Edition for session 9. Snowflake is comparison only.
- Every student has their own GCP free-trial project (their dev environment). The same Terraform deploys to any project via `project_id`. Each student keeps their own Terraform state.
- **Week 1 (sessions 1-3) is individual.** In session 3 each student gets one of seven shipper profiles; three students share each profile.
- **Teams of three form in session 4**: the three students with the same shipper profile. Their first task is to compare their three designs and agree on one. Each team picks one member's project as production.

## Assessment (as approved)
| Component | Weight |
|---|---|
| Attendance | 10% |
| Workshop checkpoints | 10% |
| Team project: build 30%, redesign 15% | 45% |
| Peer rating by other teams at the board | 10% |
| Individual performance at the board | 25% |

Hand-in: one GitHub repo per team with README, code and Terraform, a report of max 4 pages (template in `project/`), a `prompts/` folder, and a contribution statement. AI use is allowed if students can explain everything they submit.

## Repo layout
- `README.md`, `COURSE_OVERVIEW.md`: entry points for students.
- `setup/`: GCP and Databricks guides.
- `sessions/NN-<slug>/`: `README.md` (title, one-line subtitle, date, Goals, Materials), `workshop.md`, `notes.md`, `slides/` (the exported `.pptx`, named `session-NN-<slug>.pptx`), `starter/`.
- Folder slugs follow the session title. Current: `01-cloud-architecture-and-gcp-fundamentals`, `02-storing-data-in-the-cloud`, `03-architecture-patterns-lambda-vs-kappa`, then 04 to 15 as in the README schedule. When a title changes, rename the folder and update every link to it.
- `project/`: brief, report template, marking, prompts folder.
- `event-generator/`: synthetic freight data (batch files and live events). Deterministic with seed 42, so every student gets identical data. Keep its tests passing: `python3 -m unittest`.
- `architecture/`: reference architecture.

## Known updates still to make
- README "Start here" step 4 says teams form in session 3: change to session 4.
- `COURSE_OVERVIEW.md` says teams form in session 3: change to session 4, and note week 1 is individual.

## Conventions
- Workshop guides: core task, checkpoint, stretch, teardown, "if something goes wrong".
- Workshops run in Cloud Shell; don't require local installs.
- Every workshop that starts something billable ends with a teardown step.
- `notes.md` is filled after each session from the recording summary: planned, covered, questions from the room.
- Plain, short British English. All carriers, shippers and prices in the generator are fictional; never use real company data.
