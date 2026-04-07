# Symplichain Hackathon Submission

## 1. Shared Gateway Problem

### Proposed architecture

I would keep the design close to the current stack:

- Django API receives customer requests.
- Requests are written into **customer-specific queues** in Redis.
- A dispatcher or Celery-based scheduler uses **round-robin selection** across active customers.
- A single shared gateway worker layer sends outbound calls to the external API.
- A **global token bucket limiter** allows at most **3 requests per second** across all customers.
- Responses and retry metadata are stored for observability and replay safety.

### How the 3 requests per second limit is guaranteed

I would enforce the limit at the last point before the outbound HTTP call. That prevents accidental bypass from multiple workers.

Implementation choice:

- Global token bucket in Redis
- refill rate = 3 tokens per second
- bucket capacity = 3
- worker must acquire 1 token before sending a request
- if no token is available, the worker waits

This keeps the total outbound rate at 3 requests per second or lower.

### Fairness policy

I would not use one large FIFO queue, because Customer B would get stuck behind Customer A's flood.

Instead:

- maintain one queue per customer
- keep a list of active customers
- dispatch in round-robin order
- send one eligible request per customer on each pass

Result:

- Customer A can still submit 100 requests
- Customer B's 1 request gets a turn quickly
- no customer can monopolize the shared external API

### Failure handling and retries

If the external API returns a 5xx error or temporary timeout:

- retry only transient failures
- use exponential backoff: 2s, 4s, 8s
- add jitter to avoid synchronized retries
- cap retries at 3
- move permanent failures to a dead-letter queue for manual review

This protects the upstream API and gives operators a clean failure lane.

## 2. Mobile Architecture

### Recommendation

Use **React Native with TypeScript**.

### Why

- team already uses React on web
- faster delivery than separate Kotlin and Swift codebases
- shared patterns and some shared business logic
- easier hiring and maintenance for a small engineering team

### Interaction model

I would use **tap-first mobile UX** with **optional voice shortcuts**.

Reason:

- logistics workflows depend on camera capture, confirmation, and exception handling
- full speech-first interaction is harder in noisy field environments
- voice is useful for quick notes and low-friction data entry, not as the only input method

### App design principles

- camera-first POD flow
- large buttons and short task paths
- offline queue for weak networks
- background sync and retry for uploads
- simple status tracking for upload, validation, and failure recovery

## 3. CI/CD and Deployment Pipeline

I created two GitHub Actions workflows:

- `staging-deploy.yml` for pushes to `staging`
- `production-deploy.yml` for pushes to `main`

Each workflow does this:

1. Checkout code
2. Setup Python and install backend dependencies
3. Run simple smoke checks
4. Setup Node and build frontend assets
5. Upload built static assets to S3
6. SSH into EC2
7. Pull latest branch
8. Install dependencies
9. Run Django migrations
10. Run collectstatic
11. Restart gunicorn, celery, and nginx

### Improvement path with Docker and Terraform

Yes, this setup can be improved.

**With Docker:**

- consistent runtime between local, staging, and production
- easier rollback using image tags
- cleaner dependency management

**With Terraform:**

- repeatable infrastructure
- version-controlled AWS resources
- safer environment creation and change tracking

I included starter files for both as a bonus, not as a full production rollout.

## 4. Debugging the Monday Morning POD Outage

### Debugging order

#### Step 1: Check Nginx and Django logs

First question: did the upload request reach the backend at all?

Commands:

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u gunicorn -n 200 --no-pager
```

#### Step 2: Verify S3 upload stage

If Django received the request, the next question is whether the image was saved to S3.

Look for:

- boto3 errors
- IAM permission failures
- bucket policy problems
- request timeout or region mismatch

#### Step 3: Check Celery and Flower

If S3 succeeded, I would inspect whether the validation task was created and consumed.

Commands:

```bash
sudo journalctl -u celery -n 200 --no-pager
celery -A config inspect active
celery -A config inspect reserved
```

Dashboard:

- Flower for task state, retries, and failures

#### Step 4: Check Bedrock-related failures in CloudWatch

If Celery is running but tasks fail mid-processing, I would inspect Bedrock timeouts, throttling, auth issues, or model invocation failures.

#### Step 5: Check RDS write failures

If inference succeeded but final status was not saved, I would inspect:

- DB connection limits
- slow queries
- lock contention
- transaction errors in Django logs

## Deliverables included in this package

- Python fair gateway prototype
- GitHub Actions YAML workflows
- Docker and Terraform starter files
- mobile architecture note
- outage debugging runbook

