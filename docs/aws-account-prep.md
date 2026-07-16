# AWS Account Prep

This file describes what is needed before implementing the AWS portion of **OncoOmics Agent: NSCLC Atlas Edition**.

## What I Need From Your AWS Account

I do not need secrets pasted into chat. I need the local machine to be authenticated with AWS CLI.

Run or prepare to run:

```bash
aws --version
aws configure
aws sts get-caller-identity
```

The second command should return the intended AWS account and IAM identity.

If `aws --version` fails, install AWS CLI first. The repo includes `scripts/check_aws_prereqs.sh` for the local verification step.

## Recommended Region

Use:

```text
us-east-1
```

This region is broadly supported and usually convenient for demos. If you prefer another region, keep the whole project in that one region.

## IAM Permissions Needed

The IAM user or role should be able to manage project resources for:

- S3
- RDS or Aurora PostgreSQL
- IAM roles and policies for the app
- Lambda and API Gateway, if serverless is used
- CloudWatch logs
- AWS Budgets or billing alerts

Root credentials should not be used for day-to-day implementation.

## Safety Setup First

Before creating infrastructure:

- Confirm whether the account is on AWS Free plan, Paid plan with credits, or an older free-tier setup.
- Create a budget alert, recommended threshold: `$5`.
- Enable MFA on the AWS account.
- Tag resources with `project=oncoomics-agent`.
- Store credentials locally or in AWS-managed services, never in Git.

## Secrets That Must Never Be Committed

- AWS access keys
- AWS secret access keys
- database passwords
- `.env` files with real values
- controlled-access biomedical data
- raw patient-level data with restricted licenses

## Implementation Defaults

- Start local-first.
- Upload only curated public summary files to S3.
- Use the smallest practical PostgreSQL database option.
- Create read-only database credentials for the agent.
- Tear down nonessential resources if the project is paused.
