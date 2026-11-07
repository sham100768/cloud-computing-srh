# Workshop: your first cloud project

**Time:** about 55 minutes. Everyone works in their own Google Cloud account. Pair up only for step 4.

## 1. Sign up for the Google Cloud free trial
Follow [setup/gcp.md](../../setup/gcp.md). Create a project called `cc-<your-name>` and note its **project ID** (shown under the name; it may have numbers added).

## 2. Set a €50 budget alert
Search **Budgets and alerts** in the console. Create a budget of €50 and keep the 50%, 90% and 100% alerts.
A budget only sends emails. It does not stop anything running.

## 3. Create a bucket with Terraform
Open **Cloud Shell** (the `>_` icon, top right of the console). Terraform is already installed there.

```bash
git clone https://github.com/sham100768/cloud-computing-srh.git
cd cloud-computing-srh/sessions/01-from-servers-to-the-cloud/starter
gcloud config set project YOUR-PROJECT-ID
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars        # set project_id and neighbour_email, then Ctrl+O, Enter, Ctrl+X
terraform init
terraform plan               # read it: what will Terraform create?
terraform apply              # type yes
```

Then open the `bucket_url` it prints and check the bucket is there.

## 4. Add your neighbour in IAM
In `main.tf`, uncomment the `neighbour_viewer` block. Run `terraform plan`, read the change, then `terraform apply`.
Ask your neighbour to open your project in the console. They should see it, but not be able to change anything.

## Checkpoint
`terraform apply` works in your own project, and `terraform plan` now says **No changes**.

## Stretch
- Upload a file to your bucket, then try to make it public. Why does it fail?
- Create a second bucket by hand for Terraform state, uncomment the `backend "gcs"` block in `versions.tf`, and run `terraform init -migrate-state`.
- Change the region variable to `europe-west1` and run `terraform plan`. What would Terraform do, and why?

## Teardown
Nothing today bills by the hour, and an empty bucket costs nothing, so leave it: we use it on Wednesday.

## If something goes wrong
- **Card verification fails:** try another card, or finish signing up after class.
- **`Error 403` or "API not enabled":** the error message contains a link. Open it, enable the API, wait a minute, apply again.
- **"Bucket name not available":** names are global. Check `project_id` in `terraform.tfvars` is your own.
- **Wrong project:** run `gcloud config get-value project` and compare it with your project ID.
