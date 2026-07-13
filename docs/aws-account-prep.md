# AWS Account Prep

This is what we need before implementing the AWS portion.

## Required From The AWS Account

- An AWS account where you can create S3, RDS, IAM, Lambda, and budget resources.
- Console access with permission to view Billing and Cost Management.
- A default region. Recommended: `us-east-1` or the region closest to you, as long as the chosen services are available.
- AWS CLI configured locally, or willingness to configure it during implementation.

## Safety Setup First

Before creating project resources:

- Confirm whether the account is on the newer credit/free-plan model or a legacy free-tier model.
- Create an AWS Budget with email alerts.
- Enable billing alerts.
- Decide the maximum monthly spend tolerance for the project.
- Create a project-specific IAM user or role rather than using root credentials.

## Credentials We Should Not Share In The Repo

Never commit:

- AWS access keys
- secret access keys
- database passwords
- `.env` files with real credentials
- downloaded controlled-access biomedical data

Use local environment variables or AWS Secrets Manager later if needed.

## Minimum Local Checks

When implementation starts, run:

```bash
aws sts get-caller-identity
aws configure list
```

This confirms the local machine can reach the intended AWS account without exposing secrets in the repository.

## Decisions Needed Tomorrow

- AWS region to use.
- Monthly budget alert threshold.
- Whether to use RDS immediately or start with local PostgreSQL first.
- Whether the first deploy target is Lambda or a small FastAPI service.

