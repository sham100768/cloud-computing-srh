# Course overview: Cloud Computing and Data Architectures

SRH University Hamburg · Winter semester 2026 · Lecturer: Shyam Savania

## What this module is about

Most data work today runs in the cloud. In this module you learn how to design, build and run data platforms there, the way companies actually do it.

You won't just read about cloud services. Over five weeks you build a working data platform on Google Cloud, one layer per session. You then redesign it for a new business problem and defend your decisions in front of an architecture board.

Everything is tied to logistics, the industry this programme is built around.

## The case you'll work on

You are the data team at a company that sells freight analytics to shippers, the businesses moving goods by air and ocean. Your platform has two kinds of users:

- **Operations teams** need to know where their shipments are right now, and which ones are delayed.
- **Executives** want to know what they spent, which carriers are reliable, and where they can save money.

Those two needs pull in different directions: one wants data in seconds, the other wants data that is complete and accurate. Balancing them is the core of the module.

## What you'll be able to do by the end

- Explain and compare data warehouses, data lakes, and the Lambda and Kappa architectures.
- Choose the right cloud services for a problem, and justify the choice on cost, scale and performance.
- Build batch and streaming pipelines with BigQuery, Cloud Storage, Pub/Sub, Dataflow and Dataproc.
- Run Kafka and containerised applications on Kubernetes.
- Process data with Spark and PySpark, and use Databricks for analysis and machine learning.
- Define infrastructure as code with Terraform, and ship changes from development to production.
- Present technical decisions clearly, and defend them under questioning.

## How a session works

Every session runs 16:30 to 19:00 in seminar room 1.4 and follows the same shape:

| Block | What happens |
| --- | --- |
| Recap | Where your platform is, and what we add today |
| Concepts | The fundamentals for this layer |
| Industry | How this works in real companies: the tradeoffs, and what breaks |
| Break | |
| Workshop | You add today's layer to your platform |

Slides are kept short. Most of the learning happens in the workshop.

Each workshop has a **core task** most people finish in class, a **stretch task** if you're fast, and a **checkpoint branch** in this repo. If you get stuck or miss a session, you can start the next one from the checkpoint and still keep up.

## Schedule

| Week | Focus |
| --- | --- |
| 1 (16–20 Nov) | Cloud foundations, storage and BigQuery, architecture patterns |
| 2 (23–25 Nov) | Docker, Kubernetes and Kafka |
| 3 (30 Nov–4 Dec) | Streaming with Pub/Sub and Dataflow, Spark on Dataproc, Databricks |
| 4 (7–11 Dec) | Production readiness and CI/CD, project lab, the evolution brief |
| 5 (14–18 Dec) | Redesign lab and the architecture board |

Session-by-session dates and materials are in the [README](README.md). Week 3 has four sessions, so plan your time.

## The project

Week 1 (sessions 1 to 3) is individual: you each build in your own Google Cloud project. In session 3 you get one of seven shippers to serve, each with its own targets for data freshness, accuracy and cost. Three of you share each shipper.

Teams of three form in session 4: the three students with the same shipper. Your first task as a team is to compare your three designs and agree on one, then pick one member's project as production. No two teams build exactly the same thing.

The project grows out of the workshops. Each session adds a layer, so by the end of week 4 your team has a deployed platform. Along the way, expect a few real-world surprises.

At the end of week 4 you receive the **evolution brief**: a new business challenge your platform has to meet. You spend week 5 redesigning it, then present it to the architecture board.

### What you hand in

Everything goes in your team's GitHub repo, due **Tuesday 15 December**:

- **A README** that explains your platform and lets someone else run it.
- **Your code and Terraform.**
- **A report of no more than 4 pages**, using the [template](project/report-template.md). It explains your thinking: why you made your choices, what you tried, what failed and what you changed.
- **A prompts folder** with the key AI prompts you used, and what you changed in the output.
- **A contribution statement** signed by all three team members.

### The architecture board

Each team gets 30 minutes: a live demo of your platform, your redesign pitch, and questions. Anyone in the team may be asked about any part of the system, so make sure you understand all of it, not just your own piece.

## Assessment

| Component | Weight | Individual or team |
| --- | --- | --- |
| Attendance | 10% | Individual |
| Workshop checkpoints | 10% | Individual |
| Team project (build and redesign) | 45% | Team |
| Peer rating: the other teams score each presentation at the board | 10% | Team |
| Performance at the board: questions on your part and your AI use | 25% | Individual |

There is no written exam. Details are in [project/marking.md](project/marking.md).

## Using AI

You're encouraged to use AI tools; that's how the industry works now. The rule is simple: **you must be able to explain everything you submit.** Keep your key prompts in the prompts folder. At the board you may be asked to walk through them and explain your reasoning.

## Accounts and cost

You need two accounts before session 1. Both are free:

- **Google Cloud free trial:** follow [setup/gcp.md](setup/gcp.md). It gives you $300 of credit for 90 days. A card is needed to verify your identity, but you won't be charged unless you upgrade.
- **Databricks Free Edition:** follow [setup/databricks.md](setup/databricks.md). No card needed.

Some cloud services bill for every hour they run, even when you're not using them. **Every workshop ends with a teardown step. Do it every time**, or you'll burn through your credit.

## What to bring

A laptop with a modern browser and a GitHub account. Most work happens in the browser and Google Cloud Shell, so you don't need to install much locally.

## Questions

Ask in class, or message me on Teams.
