# Session 1 notes

## Planned
- How the module works: the project, the architecture board and how you're assessed.
- Compute, network and storage, and how infrastructure moved from on-premise to virtualisation to the cloud.
- Google Cloud basics: organisations, folders, projects, billing, regions and zones.
- IAM: least privilege, user accounts and service accounts.
- Storage types and compute options, and the shape of a modern data platform.
- Terraform, and how code reaches production.
- Workshop: your own Google Cloud project, a budget alert, a bucket created with Terraform, and IAM access for your neighbour.

## What we covered

### How the module works
- Marks: attendance 10%, the project 55% (your platform 40%, your redesign 15%), and you at the architecture board 35%. There's no written exam. Details are in [project/marking.md](../../project/marking.md).
- Weeks 1 to 4 teach the services and build your platform end to end. On Thursday 10 December you get a brief that changes the requirements, and you redesign your platform for it. You hand in on Sunday 13 December and present it at the board on 14 or 16 December. (Dates updated after the schedule changed.)
- On Friday (session 3) each of you gets a shipper: a fictional company with its own priorities, such as cost, how fresh the data is, or reliability. Your designs are judged against those priorities. A design that costs several times more for a shipper focused on cost will count against you.
- The board works like a real architecture review: you present, the other students on your shipper ask the questions, and you defend your decisions.
- AI use is encouraged. What's assessed is your judgement and your decisions, so keep a record of how you used AI (see [project/prompts/](../../project/prompts/)).
- Each session is about 1.5 hours of lecture and 1.5 hours of workshop. This week's workshops are lighter; they ramp up from next week.

### Cloud fundamentals
- Every system has three building blocks: compute, network and storage.
- On-premise meant owning the hardware: high upfront cost, and buying for peak load so most capacity sat idle. Virtualisation put many virtual machines on shared hardware through a hypervisor. The cloud providers rent that capacity out.
- What the cloud gives you: resources on demand, elastic scaling (a sports streaming service on match day), and metered billing.
- "Lift and shift", moving workloads unchanged, often cost more than on-premise because it used none of those benefits.
- Building to work on every provider avoids lock-in, but means you never use any one provider fully. It's a trade-off.
- The service models run from on-premise to IaaS, PaaS and SaaS: the further along, the less you own and manage. Regulated and government organisations often stay close to IaaS or on-premise; start-ups usually start with PaaS and SaaS.

### Google Cloud and IAM
- The hierarchy is organisation, folders, projects. Folders often map to departments, and billing can be split per folder or project.
- Regions and zones matter for resilience and for how fast users reach the data.
- IAM always follows least privilege: who (the principal), what they can do (view, edit, own, delete), and on which resource. Start-ups often grant at project level; finance and government go down to a bucket or a file. More granularity means more complexity, so automate it.
- User accounts are for people. Service accounts are for applications, and need more thought when several customers' data sits on one platform. Never download service account keys in production: a key is a backdoor, and auditors will flag it.

### Storage, compute and the data platform
- Five storage types: object, block, file, database and warehouse. Every provider has a version of each. Know when to use each one; the product names you can look up. Session 2 goes into them in depth.
- Compute, from most to least to manage: virtual machines (you manage the operating system), containers (Docker, Kubernetes, or managed services such as GKE), and serverless (event-driven or batch, usually cheapest for small workloads).
- A modern data platform runs ingest, store, process, serve. ETL and ELT differ in where the transform happens.

### Terraform and getting to production
- Terraform is the industry standard for infrastructure as code. `main.tf` describes what you want, `terraform plan` shows the difference from what's live, and `terraform apply` makes it so.
- Code reaches production through a pull request, then dev, then test with test data, then production.
- Testing containers is easy. Catching bad data, such as malformed files or a price that's wrong, is where most data teams struggle and overspend.
- How AI is changing the development life cycle comes later in the module.

### Workshop
Sign up for Google Cloud, set a €50 budget alert, sign up for Databricks Free Edition, create a bucket with Terraform, and give your neighbour viewer access through IAM. The steps are in [workshop.md](workshop.md).

## Questions from the room
- **Will we cover MCP and AI agents?** They're not part of the core module, which is about data architectures and cloud computing. If there's time once the core topics are done, we'll cover the basics: MCP servers, how to connect to them, and how to build agents.
- **When is the redesign decided, and how is it marked?** You get the brief, then decide how to change your architecture. More detail on what you're marked on comes in session 2.
- **What if I didn't bring a laptop?** Pair up with someone this week. Next week's workshops need your own laptop.
