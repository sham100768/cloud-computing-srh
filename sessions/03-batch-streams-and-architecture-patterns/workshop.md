# Workshop: your first design

**Time:** about 80 minutes, on your own, in Cloud Shell and your browser. You need Wednesday's `freight` dataset in BigQuery, including your `schedules` table. The steps are the same on your own account and on the course account.

Today you get your launch customer: the shipper whose contract sets your platform's targets. You measure how its carriers perform, and make your first architecture decision. Everything goes in your own fork of the course repo, which from today is your project.

## 1. Fork the repo and get your launch customer (10 min)

1. On GitHub, open [the course repo](https://github.com/sham100768/cloud-computing-srh) and click **Fork**. Keep the name `cloud-computing-srh`.
2. In Cloud Shell, point your existing copy at your fork, and keep the course repo as `upstream`:

   ```bash
   cd ~/cloud-computing-srh
   git remote rename origin upstream
   git remote add origin https://github.com/<your-github-username>/cloud-computing-srh.git
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   git config --global credential.helper 'cache --timeout=36000'
   ```

   From now on, `git pull upstream main` gets new course material, and `git push origin main` saves your work to your fork.
3. To push from Cloud Shell, GitHub needs a token instead of your password. On GitHub go to **Settings → Developer settings → Personal access tokens → Fine-grained tokens**, and create one for your fork only, with **Contents: read and write**. Paste it when `git push` asks for a password.
4. Find your first name on the **Who has which launch customer** slide. Then look up your customer in [project/shippers.md](../../project/shippers.md) and write down its ID, its lanes and its three targets: freshness, reliability and budget.
   - **Today's slides:** on GitHub, open [`slides/`](slides/), click the `.pptx` file, then click **Download raw file** (the download icon at the top right of the file).
   - **Your customer's profile:** `project/shippers.md` is already in your copy of the repo. Open it in Cloud Shell with `cloudshell edit ~/cloud-computing-srh/project/shippers.md`, or download it from GitHub the same way.

## 2. Delay per lane (25 min)

How reliable are the carriers your launch customer actually books? Measure it, lane by lane.

1. Open `starter/delay_per_lane.sql`. It joins `bookings` to `schedules` on `schedule_id` and works out, per lane, the average arrival delay and the share of shipments that arrived on time (no more than 24 hours late).
2. Fill in the one blank: your launch customer's shipper ID.
3. Paste it into the BigQuery console, dry-run it, then run it.
4. Create `docs/metrics.md` in your fork with a table of the results. Add your launch customer's reliability target next to each lane's on-time rate, and mark each lane as meeting the target or not.

```bash
mkdir -p ~/cloud-computing-srh/docs
cloudshell edit ~/cloud-computing-srh/docs/metrics.md
```

Which lanes miss the target? Which carriers serve them? Keep the numbers: they're your evidence in step 4.

## 3. Architecture diagram (20 min)

Start from the reference platform in today's slides and in [architecture/](../../architecture/), and adapt it to your launch customer. This is your company's platform; your launch customer decides which parts must be live.

- Mark every box as **live** (must meet your freshness target) or **batch** (can run on a schedule).
- Add anything your launch customer needs that the reference doesn't have, and cross out anything it doesn't need.
- Any tool is fine: a photo of a paper sketch, draw.io, or a Mermaid diagram in Markdown.

Commit it to `docs/architecture/` in your fork. A photo is easiest to upload on GitHub in the browser: open your fork, **Add file → Upload files**, and put it in `docs/architecture/`. Then run `git pull origin main` in Cloud Shell so your copy has it too.

## 4. ADR 001: Lambda or Kappa (20 min)

Copy the [ADR template](../../project/adr-template.md) to `docs/adr/001-<slug>.md`, for example `docs/adr/001-processing-pattern.md`, and decide: should your platform follow Lambda or Kappa?

- **Context:** your launch customer, its three targets, and your delay numbers from step 2.
- **Options:** at least Lambda and Kappa, and what each would mean for your launch customer.
- **Decision and consequences:** cost, freshness, complexity, and what gets harder.

Either answer can be right. What matters is that your reasons come from your launch customer's targets and your evidence.

Three questions help you decide:

1. **Freshness.** Does your launch customer need a live path at all? An hour can be met by loading files often. 60 seconds can't.
2. **Sources.** Rates and schedules arrive as daily files, and tracking arrives as events. Mixed sources point to Lambda. Kappa only fits if everything can be treated as an event.
3. **Budget.** $20 to $60 a month is tight. Check what an always-on service, such as a Kafka cluster or a streaming Dataflow job, would cost in the [pricing calculator](https://cloud.google.com/products/calculator) before you choose it. Pub/Sub writing straight into BigQuery is a cheap live path.

A strong ADR has:

- your launch customer's three targets, and real numbers from `docs/metrics.md`;
- both options, applied to your launch customer rather than in general;
- a rough monthly cost;
- at least one honest downside of the option you chose.

"Kappa is more modern" or "Lambda is more complete" isn't a reason on its own. Tie every reason to a target or a number.

Save your work. `git add -A` takes everything you've changed, including your `schedules` table from Wednesday and today's SQL, not just `docs`. Your Terraform state and `terraform.tfvars` stay out: `.gitignore` excludes them.

```bash
cd ~/cloud-computing-srh
git add -A
git status          # check the list: docs, .tf and .sql files, no tfstate or tfvars
git commit -m "Session 3: metrics, diagram, ADR 001"
git push origin main
```

## Checkpoint

Your fork on GitHub contains:

- `docs/metrics.md`, with delay and on-time rate per lane next to your reliability target
- a diagram in `docs/architecture/`
- `docs/adr/001-*.md`

## Stretch

- **Cost check.** Add a rough monthly cost estimate to ADR 001, box by box, using the [Google Cloud pricing calculator](https://cloud.google.com/products/calculator). Does your design fit your launch customer's budget? If not, what would you change?

## Teardown

Stop anything that bills by the hour before you leave.

## If something goes wrong

- **`Not found: Table ...:freight.schedules`**: you haven't created the `schedules` table yet. Do step 3 of Wednesday's workshop (the TODO in `main.tf`), then run `./load.sh` again.
- **`No matching signature for function DATETIME_DIFF`**: your `schedules` table has the arrival columns as `STRING`. They must be `DATETIME`: fix the type in `main.tf`, run `terraform apply`, and reload with `./load.sh`.
- **`Authentication failed`** or **`Permission denied`** on `git push`: paste the token as the password, not your GitHub password, and check it has write access to your fork.
- **Repo folder gone:** see the [Cloud Shell tips](../../setup/gcp.md#cloud-shell-tips), then clone again.
- **`fatal: No such remote 'origin'`** or **`remote upstream already exists`**: you've already run part of step 1. Run `git remote -v` to see what you have.
