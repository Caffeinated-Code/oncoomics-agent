# AWS Groundwork

This folder contains deployment groundwork for the AWS version of **OncoOmics Agent: NSCLC Atlas Edition**.

The first AWS build should be small:

- S3 stores curated source files and manifests.
- PostgreSQL stores summary tables, not raw single-cell matrices.
- Lambda/API Gateway or a small backend queries the database later.
- AWS Budgets and tags are created before data services.

## Deployment Order

Do not deploy the database first. Use this order:

1. Install and configure AWS CLI.
2. Confirm account identity and region.
3. Deploy the budget template.
4. Deploy the S3 storage template.
5. Choose exactly one database template:
   - Aurora PostgreSQL Serverless for the newer AWS Free plan.
   - RDS PostgreSQL micro instance for legacy or paid-plan free-tier-compatible accounts.
6. Load only curated summary tables.

## Current Local Status

AWS CLI was not available when this groundwork was added. Install it before deploying:

```bash
aws --version
aws configure
aws sts get-caller-identity
```

## Recommended Defaults

- Region: `us-east-1`
- Budget: `$5`
- Project tag: `project=oncoomics-agent`
- Environment: `dev`
- Data policy: public, processed, non-controlled data only

## Cost Strategy

The project should avoid raw matrix storage in PostgreSQL. Raw `.h5ad` or large source files belong outside Git and can be kept locally or in S3 only when needed. The database should contain compact summary tables such as expression by gene, cell type, dataset, and sample group.

