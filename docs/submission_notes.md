# Submission notes

## What I built

This project focuses on the parts that benefit from code and concrete implementation:

- A fair request pooling and throttling prototype for the shared external API problem
- Two GitHub Actions deployment workflows matching the staging and production branch model
- Supporting DevOps starter files for Docker and Terraform
- A mobile architecture note and an outage debugging runbook

## Why this package is practical

The challenge asked for clear reasoning and cost-conscious design. Instead of proposing a large distributed platform, this package stays close to the given stack:

- Redis-compatible queueing pattern
- Celery-friendly worker design
- EC2 + S3 + GitHub Actions deployment path
- incremental improvement path toward Docker and Terraform

## What to mention during submission

- The Python gateway code is a prototype to show fairness and throttling logic.
- In production, queue state would live in Redis and workers would run as Celery consumers.
- The workflows assume GitHub secrets and EC2 systemd services already exist.
- Docker and Terraform are included as a bonus starter, not a full production rollout.
