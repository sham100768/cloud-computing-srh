# Course overview: Cloud Computing and Data Architectures

SRH University Hamburg · Winter semester 2026 · Lecturer: Shyam Savania

## What this module is about

Most data work today runs in the cloud. In this module you learn how to design, build and run data platforms there, the way companies actually do it.

You won't just read about cloud services. Over five weeks you build a working data platform on Google Cloud, one layer per session. You then redesign it for a new business problem and defend your decisions in front of an architecture board.

Everything is tied to logistics, the industry this programme is built around.

## The case you'll work on

You are the data team at a company that sells freight analytics to shippers, the businesses moving goods by air and ocean. Your company builds one platform and sells it to many shippers. Its users come in two kinds:

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
- Explain where AI fits on a data platform, and build a simple assistant over your own data.

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

Each workshop has a **core task** most people finish in class, a **stretch task** if you're fast, and a **checkpoint** that lists what you should have by the end. If you get stuck or miss a session, ask me and we'll get you back on track.

## Schedule

| Week | Focus |
| --- | --- |
| 1 (16–20 Nov) | Cloud foundations, storage and BigQuery, architecture patterns |
| 2 (23–25 Nov) | Docker, Kubernetes and Kafka |
| 3 (30 Nov–4 Dec) | Streaming with Pub/Sub and Dataflow, Spark on Dataproc, Databricks |
| 4 (7–11 Dec) | Production readiness and project lab, the evolution brief, the redesign lab |
| 5 (14–18 Dec) | The architecture board, then recap and AI foundations |

Session-by-session dates and materials are in the [README](README.md). Week 3 has four sessions, so plan your time.

## The project

The project is individual: you each build your own platform in your own Google Cloud project. In session 3 you each get a launch customer: one of seven shippers, your company's first big contract. Its targets for data freshness, carrier reliability and monthly budget are what your company promised, and your version of the platform has to meet them. Three of you share each launch customer, but each of you builds and defends your own design, so no two platforms are exactly the same.

The project grows out of the workshops. Each session adds a layer. By the end of week 3 you have built both a Lambda and a Kappa version of your platform, and by the end of week 4 a deployed platform. Along the way, expect a few real-world surprises.

In week 4 you receive the **evolution brief**: a new business challenge your platform has to meet. You redesign your platform for it before the architecture board at the start of week 5.

### What you hand in

Everything goes in your fork of this repo, due **Sunday 13 December**:

- **A README** that explains your platform and lets someone else run it.
- **Your code and Terraform.**
- **A report of no more than 4 pages**, using the [template](project/report-template.md). It explains your thinking: why you made your choices, what you tried, what failed and what you changed.
- **A prompts folder** with the key AI prompts you used, and what you changed in the output.

### The architecture board

Each of you gets about 10 minutes: a live demo of your platform, your redesign pitch, and questions. Students present grouped by launch customer, shippers 1 to 4 on 14 December and 5 to 7 on 16 December, so the three designs for each customer come back to back. Your board is the other two students with your launch customer, plus me. They already know the customer, so no time goes on context: they ask the questions, and I do the scoring.

## Assessment

| Component | Weight |
| --- | --- |
| Attendance | 10% |
| Project: your platform (40%) and its redesign (15%) | 55% |
| Performance at the board: questions on your project and your AI use | 35% |

Every component is individual.

There is no written exam. Details are in [project/marking.md](project/marking.md).

## Using AI

You're encouraged to use AI tools; that's how the industry works now. The rule is simple: **you must be able to explain everything you submit.** Keep your key prompts in the prompts folder. At the board you may be asked to walk through them and explain your reasoning.

## Accounts and cost

You need two accounts before session 1. Both are free:

- **Google Cloud:** follow [setup/gcp.md](setup/gcp.md). Use the free trial on your own account: $300 of credit for 90 days. A card is needed to verify your identity, but you won't be charged unless you upgrade.
- **Databricks Free Edition:** follow [setup/databricks.md](setup/databricks.md). No card needed.

Some cloud services bill for every hour they run, even when you're not using them. **Every workshop ends with a teardown step. Do it every time**, or you'll burn through your credit.

## What to bring

A laptop with a modern browser and a GitHub account. Most work happens in the browser and Google Cloud Shell, so you don't need to install much locally.

## Questions

Ask in class, or message me on Teams.
