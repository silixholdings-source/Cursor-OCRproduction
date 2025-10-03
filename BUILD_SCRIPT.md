# BUILD_SCRIPT.md — Production Blueprint (with rigorous testing & fast error-recovery instructions for Cursor)

> Purpose: a single, executable blueprint you can paste into Cursor (or any AI-coding IDE) so the entire platform is **built with tests first, validated at every phase,** and delivered with automated CI/CD, observability, and fast error-fix feedback loops. This makes the *building phase painless* and reliable for enterprise delivery.

---

## 1 — How to use this file (quick)
1. Paste the **Master Prompt Doc** (you already have) into Cursor as project/system context.
2. Paste sections below as **step-by-step prompts** (one block per step). Each step instructs Cursor to generate code **and** a comprehensive test suite for that step.
3. Commit often. Cursor should create complete files + tests + migration + CI.
4. Run CI locally/in staging and use the “failing test → fix → re-run” loop described below.

---

## 2 — Development principles enforced by Cursor
- **Test-first where feasible (TDD):** New feature = failing test(s) first, then production code to make tests pass.
- **Atomic PRs / Small increments:** Each prompt generates a single vertical slice (API + model + tests + docs). Keep changes small.
- **CI gating:** All PRs must pass unit/integration/E2E before merge.
- **Observability by default:** Instrumentation (OpenTelemetry), structured logs, Sentry / error-reporting stubs in all services.
- **Idempotency & safe defaults:** Posting operations must be idempotent; adapters must be retried with exponential backoff.

---

## 3 — Phase-driven test plan (Cursor instructions per phase)

### Phase A — Project scaffold (Prompt + Tests)
**Cursor prompt (paste):**
```
Create project scaffold (monorepo) with backend/web/mobile directories, Docker Compose, and CI skeleton.
Also generate tests that assert:
- Backend container starts and responds to /health
- Web app route / returns 200
- Mobile app builds (type-check placeholder)
Implement GitHub Actions workflow that runs these smoke tests.
Output: Dockerfiles, docker-compose.yml, GitHub Actions config, and unit-tests for health checks.
```
**Acceptance:** `pytest` smoke tests and CI job pass locally.

---

### Phase B — Auth & Multi-Tenant bootstrap
**Cursor prompt (paste):**
```
Generate FastAPI auth module (JWT + refresh tokens + user model + company/tenant model).
Write unit tests to cover:
- signup/login/token refresh flows
- tenant isolation: user of tenant A cannot access tenant B resources
- pydantic validation
Include pre-commit hooks, lint config, and coverage target >= 85%.
```
**Acceptance:** Auth tests pass; CI enforces coverage.

---

### Phase C — Data models + Migrations + Golden DB seed
**Cursor prompt (paste):**
```
Create SQLAlchemy models (Invoice, InvoiceLine, Company, User, AuditEvent, TenantSubscription) and Alembic migrations.
Add tests using testcontainers (or sqlite fallback) to ensure migrations run, schema matches models, and seeded 'golden' test tenant exists.
Include seed script that loads 20 golden invoices (various layouts) used for OCR regression tests.
```
**Acceptance:** Migration + seed run in CI, seed data available for OCR/E2E pipelines.

---

### Phase D — OCR pipeline + Golden documents testing
**Cursor prompt (paste):**
```
Add OCR worker (Celery) with adapter for Azure Form Recognizer (abstract interface). Create a local "mock OCR" adapter for tests. Create a test harness:
- Auto-upload the 20 golden PDFs/images
- Run extraction pipeline
- Assert field-level accuracy thresholds:
   - Invoice total: >= 98% match
   - Supplier detection: >= 95%
   - At least 90% of invoices have usable line-item extraction (or fallbacks flagged)
Write tests that compare OCR output to expected JSON fixtures and fail if below thresholds.
```
**Acceptance:** OCR regression tests pass; failing results captured with diff output.

---

### Phase E — 3-Way Match logic + PO/Receipt mocks
**Cursor prompt (paste):**
```
Implement 3-way match service:
- Interface: match(invoice, po, receipts) => result (matches, mismatches, confidence)
Create mocked ERP PO + receipt provider for tests. Write unit and integration tests covering:
- Perfect match (passes)
- Price mismatch (flagged)
- Qty over-receipt (flagged)
- Partial receipt (partial match)
Add logic that returns structured reasons and suggested resolutions.
```
**Acceptance:** All match scenarios covered by tests; clear resolution steps returned.

---

### Phase F — ERPAdapter + Mock Connectors + Contract tests
**Cursor prompt (paste):**
```
Create ERPAdapter interface and adapters:
- GPAdapter stub (local REST mock)
- D365BCAdapter stub
- XeroAdapter mock
Create contract tests that:
- Post approved invoice payload to adapter mock
- Adapter returns standardized response {status, erp_doc_id, method}
Write tests for idempotency: repeated post attempts with same id must not create duplicates.
Add health-check endpoints and adapter versioning checks.
```
**Acceptance:** Contract tests succeed; idempotency tests pass.

---

### Phase G — Approvals workflow & multi-step approval tests
**Cursor prompt (paste):**
```
Implement Workflow engine (rules-based) with unit tests:
- Simple approval (single approver)
- Threshold-based multi-step (manager -> finance)
- Delegation (away delegate)
- Out-of-office routing
Write integration tests that simulate multiple users approving, with audit logs created for each action.
```
**Acceptance:** Workflow tests pass and audit logs are immutable.

---

### Phase H — Mobile flows (capture → review → approve)
**Cursor prompt (paste):**
```
Generate React Native (Expo) screens and local E2E tests (Detox or Cypress mobile emulation) that:
- Launch app, login stub, capture image (use fixture), upload, navigate to review screen, and simulate approve.
- Offline queue test: simulate network loss during upload, ensure queue persists and syncs on restore.
Add unit tests for OfflineSync module.
```
**Acceptance:** Mobile E2E tests pass in CI pipelines (or at minimum in staging runners).

---

### Phase I — Billing & Subscriptions tests
**Cursor prompt (paste):**
```
Implement TenantSubscription model + Stripe Billing integration (use stripe-mock for tests).
Write tests for:
- Trial start/end behaviors
- Webhook handling (customer.subscription.created / invoice.paid / payment_failed)
- Admin toggle ENABLE_PAYMENTS behavior (when OFF: block payment flows; when ON: allow)
- Usage-based metered billing calculation tests
```
**Acceptance:** Billing tests pass with webhook simulations.

---

### Phase J — Security, load & resilience testing
**Cursor prompt (paste):**
```
Add security tests:
- SAST checks (bandit-like stub)
- OWASP Top 10 static checks
Add load tests (k6 or locust script):
- Simulate concurrent OCR uploads (1000/min)
- Simulate 200 concurrent approver reads
Add resilience tests:
- Kill worker then restart: ensure jobs resume and no duplicates
- Simulated GP connector downtime: ensure retry/backoff and dead-lettering
```
**Acceptance:** Load tests give baseline metrics and resilience tests produce no data loss; create runbook if thresholds exceeded.

---

## 4 — CI/CD & gating (Cursor must produce these)
- **GitHub Actions** with stages:
  - Lint & unit tests
  - DB migrations test
  - Integration tests (with test DB via testcontainers)
  - E2E / smoke test stage (staging only; optional)
  - Build Docker images
  - Deploy to Staging (auto on merge to main)
  - Manual approval → Deploy to Production
- **Gates**: must pass unit+integration before builds; must pass security scan before production deploy.

Cursor prompt for CI:
```
Generate GitHub Actions pipeline described above; include matrix runs for python versions and node versions; include caching for dependencies; create secrets placeholders for Stripe, SSO, KMS.
```

---

## 5 — Fast error detection & automated fix loop (Cursor-assisted)
Add to every CI job:
- On test failure, Cursor must:
  1. Produce a **diagnostic report** listing failing tests, stack traces, and likely root causes (based on stack trace and code).
  2. Generate **candidate patches** (code changes + tests) to fix the failures, as PR drafts (branch + commit).
  3. Attach suggested unit tests if missing.
  4. Create a failing-test-to-fix checklist for the developer.

Cursor prompt for CI failure handling:
```
When tests fail, run diagnostics; create a suggested PR with fix and unit test; include explanation and risk notes; run tests in CI again; if still failing, output step-by-step debug actions.
```
> Note: this assumes Cursor can create branches/PRs in your environment; if not, it should output a ready-to-apply patch and exact `git` commands.

---

## 6 — Test data, fixtures & “golden documents”
- Maintain a `tests/golden/` directory with:
  - 50 representative invoices (varied layouts, currencies, VAT scenarios)
  - Expected JSON extractions for each (“oracle” fixtures)
- OCR regression job: on each PR or nightly, run OCR against golden set and fail if accuracy drops below configured thresholds. Cursor must produce diffs for failed fields.

---

## 7 — Observability + Postmortem readiness
- Cursor must scaffold observability:
  - OpenTelemetry traces in backend and workers
  - Metrics for queue length, job latency, OCR accuracy, posting success
  - Sentry integration (errors + breadcrumbs)
- Cursor should generate a **runbook template** for common issues (GP connector down, OCR provider quota exhaustion, failed Stripe webhook). Include immediate mitigation steps and contact lists.

---

## 8 — Developer DX to reduce pain
Ensure Cursor also generates:
- `devcontainer.json` for VS Code Codespaces / Dev Containers
- `Makefile` with common commands: `make start`, `make test`, `make seed`, `make e2e`
- Local test scripts that bring up test DBs automatically
- Clear `CONTRIBUTING.md` with commit message conventions, PR checklist, and branching model
- Pre-commit hooks (black, isort, eslint) and an autofix CI job

Prompt snippet:
```
Create devcontainer.json, Makefile, CONTRIBUTING.md, and pre-commit hooks that autoformat and run tests locally. Include common debugging commands.
```

---

## 9 — Acceptance Criteria & Definition of Done (enforced per PR)
Every PR must include:
- ✅ Unit tests (coverage >= 85% for modified code)
- ✅ Integration tests where DB/external integrations changed
- ✅ Linter passes (auto-fixed or explained)
- ✅ CI green
- ✅ Migration scripts (if DB changes)
- ✅ Updated API docs / OpenAPI schema changes
- ✅ A changelog entry for the feature

Cursor prompt:
```
When generating code, also generate a PR template that enforces the above checklist and auto-populates the PR description with test commands and acceptance criteria.
```

---

## 10 — Release / Rollback plan
- Use **canary releases**: small % of traffic to new version, monitor errors & metrics, then ramp.
- Create automatic **rollback** steps in GitHub Actions if errors breach SLOs.
- Cursor should create a rollback script and a short playbook.

Prompt:
```
Generate a canary deployment job (GitHub Actions + Kubernetes manifests) and a rollback job that reverts to last stable image if SLOs breached.
```

---

## 11 — Security, scanning & compliance (auto in CI)
- Static analysis (bandit), dependency scanning (dependabot), secret scanning, SAST.
- Cursor must add GitHub Action jobs to run these scans and fail build on critical findings.
- Include automated policy-as-code checks (e.g., terraform plan validations) before infra deploys.

---

## 12 — QA & UAT process
- Cursor must scaffold a **QA checklist** and a set of **User Acceptance Tests (UAT)**:
  - End-to-end invoice posted flow with GP and D365 mocks
  - Billing/trial expiry flows
  - SSO & SCIM provisioning
  - Mobile offline approvals
- Include test runbook for QA team and a release sign-off template.

---

## 13 — Prompts you can paste (copy/paste-ready)

**TDD Scaffold (for any new feature):**
```
You are an expert developer. For feature "<feature-name>", generate:
1) failing unit test(s) that define expected behavior,
2) production code to make the test pass,
3) any required DB migration,
4) documentation snippet and API spec update,
5) CI update if needed.
Run tests locally and output results. If failing, propose patches until green.
```

**OCR Regression Prompt:**
```
Run OCR regression:
- Use tests/golden/*.pdf
- Run current OCR pipeline
- Compare output to fixtures
- Produce a report of mismatches and suggested LLM prompt adjustments or OCR pre-processing improvements
- Fail CI if accuracy thresholds not met
```

**Adapter Contract Test Prompt:**
```
Generate contract tests for ERPAdapter interface:
- Tests that assert standard response structure across GPAdapter, D365Adapter, XeroAdapter
- Include idempotency test (posting same invoice twice)
- Include health-check tests
```

**CI Failure Auto-fix Prompt:**
```
When CI job <job-name> fails with tests X, produce:
- a diagnostic summary
- a set of 1-3 candidate code patches with rationale
- unit tests to verify the fix
- commands to apply patch and re-run CI locally
```

---

## 14 — Final checklist before handing to Cursor
- Ensure Master Prompt Doc is pasted as system context.
- Paste this BUILD_SCRIPT.md into Cursor as a high-priority instruction.
- Start with Phase A and **only move to next phase when CI/acceptance criteria pass**.
- Run nightly OCR regression and load tests in staging.

---

## 15 — Final notes (what Cursor must ALWAYS do)
- Generate **complete files**, not fragments.
- Always include tests for any new behavior.
- For external integrations, always create a **mock adapter** and **contract tests**.
- If tests fail, produce an actionable PR or a clear patch + explanation.
- Keep commits small and messageful.
- Produce human-readable runbooks for every failure mode.

---

If you want, I can now:
- 1) produce the **first Cursor prompt block** (Phase A) so you can paste it and start the project immediately, and
- 2) generate additional helper files (devcontainer, Makefile, CI) into a downloadable zip.
