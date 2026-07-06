# Terraform Drift Detector ADK Agent

Reviews Terraform Cloud refresh-only plan output and reports whether remote
infrastructure has drifted from Terraform state/configuration.

The GitHub Actions workflow runs:

```bash
terraform plan -refresh-only -detailed-exitcode -no-color
python run_drift_review.py < drift-plan.txt
```

If the agent returns `drift_detected: true`, the workflow sends
`discord_message` to the configured Discord webhook secret.

Required GitHub secrets:

```text
GOOGLE_API_KEY
TFC_TOKEN
DISCORD_WEBHOOK_URL
```

Terraform Cloud target:

```text
organization: devops_vv
workspace: agents
```
