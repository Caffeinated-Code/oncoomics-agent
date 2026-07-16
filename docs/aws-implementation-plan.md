# AWS Implementation Plan

## Summary

The AWS build should use the smallest services that prove the architecture: S3 for curated files, PostgreSQL for compact summary tables, and a read-only API for the agent. The project should not run expensive analytics infrastructure in v1.

## Free-Tier-Aware Design

AWS Free Tier now depends on account age and plan. Newer accounts can receive credits and may use a Free plan with selected services. Older accounts may follow the legacy 12-month free tier model. Confirm the account status before deployment.

Recommended database choices:

- **New AWS Free plan:** evaluate Aurora PostgreSQL Serverless if available under the account's Free plan limits.
- **Legacy or paid-plan minimal build:** use RDS PostgreSQL `db.t4g.micro` or `db.t3.micro` only if it is free-tier-compatible for the account.
- **Local-first fallback:** use local PostgreSQL until the curated summary tables are stable.

## Resource Order

1. Configure AWS CLI locally.
2. Confirm account identity with `aws sts get-caller-identity`.
3. Create a budget alert.
4. Create S3 storage for curated files.
5. Deploy one PostgreSQL option.
6. Load summary tables.
7. Add backend/API resources only after SQL queries are validated.

## CloudFormation Templates

- `infra/cloudformation/00-budget.yaml`: monthly cost alert.
- `infra/cloudformation/01-storage.yaml`: private encrypted S3 bucket.
- `infra/cloudformation/02-rds-postgres-micro.yaml`: minimal RDS PostgreSQL option.
- `infra/cloudformation/03-aurora-postgres-serverless.yaml`: Aurora PostgreSQL Serverless option.

Only one database template should be deployed.

## AWS CLI Setup

Install AWS CLI, then run:

```bash
scripts/check_aws_prereqs.sh
```

The local machine currently needs AWS CLI installed before deployment work can continue.

## Deployment Commands

Budget:

```bash
aws cloudformation deploy \
  --stack-name oncoomics-budget-dev \
  --template-file infra/cloudformation/00-budget.yaml \
  --parameter-overrides BudgetLimitUSD=5 AlertEmail=you@example.com \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

Storage:

```bash
aws cloudformation deploy \
  --stack-name oncoomics-storage-dev \
  --template-file infra/cloudformation/01-storage.yaml \
  --parameter-overrides BucketName=oncoomics-agent-dev-CHANGE-ME Environment=dev \
  --region us-east-1
```

Database deployment should wait until the VPC/subnet/security group choices are confirmed.

## Cost Controls

- Keep database storage small.
- Store only summary tables in PostgreSQL.
- Keep raw downloaded atlas files out of Git.
- Tag every resource with `project=oncoomics-agent`.
- Use private database networking.
- Use read-only database credentials for the future agent.
- Delete or snapshot database resources when pausing work.

## Data Size Target

The first AWS database should stay compact:

- gene panel: 20-50 genes
- summary rows: gene x cell type x source/sample group
- raw matrix files: not loaded into PostgreSQL
- database target: comfortably below 1 GB if using Aurora Free plan constraints

## Sources

- [AWS Free Tier](https://aws.amazon.com/free/)
- [AWS Free Tier plans](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html)
- [RDS Free Tier](https://aws.amazon.com/rds/free/)
- [AWS Lambda pricing](https://aws.amazon.com/lambda/pricing/)

