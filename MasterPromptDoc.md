# MasterPromptDoc.md — AI Invoice Automation Enterprise SaaS

> This document defines the **Master Prompt Doc** for building a world-class, enterprise-grade AI-powered invoice automation SaaS.  
> It is designed to be used as a **system-level context** in AI coding IDEs like Cursor, Replit, or Lovable to generate a production-ready, multi-platform application.  
> Together with BUILD_SCRIPT.md, it ensures reliable, test-driven development with enterprise scalability.

---

## 1. Vision & Positioning
- Build a **multi-ERP invoice automation platform** that extracts, validates, and posts invoices with AI assistance.  
- Competitors: Tipalti, Bill.com, Stampli, Yooz.  
- Differentiator: AI Copilot, multi-ERP abstraction layer, advanced vendor management, compliance packs, subscription flexibility, extensibility.  
- Target: Mid-market to enterprise (finance/AP teams, global operations).  

---

## 2. Core Application Features
1. **Invoice Processing AI**
   - OCR extraction (line items, totals, supplier detection).  
   - AI-based GL coding & cost allocation.  
   - Fraud detection & anomaly scoring.  
   - AI-powered approval chain recommendations.  

2. **ERP Integration (Multi-ERP Adapter Layer)**
   - Microsoft Dynamics GP.  
   - Dynamics 365 Business Central.  
   - Sage, Xero, QuickBooks.  
   - Extensible adapter framework for future connectors.  

3. **Workflows**
   - Multi-step approvals with thresholds.  
   - Delegation & out-of-office routing.  
   - In-app chat linked to invoices with AI summaries.  

4. **Mobile App**
   - iOS & Android (React Native Expo).  
   - Offline approvals.  
   - Camera capture → OCR pipeline.  
   - Push notifications for approvals & trial reminders.  

5. **Web App**
   - Next.js with Tailwind + shadcn/ui.  
   - Dashboard, analytics, workflow management.  
   - Admin console for billing, users, roles.  

6. **Security & Compliance**
   - Role-based access control.  
   - SOC2-ready audit logs (immutable).  
   - GDPR/POPIA retention policies.  
   - Optional blockchain anchoring for immutable approvals.  

---

## 3. Subscription & Monetization Strategy
- **Core subscription tiers**: Basic / Pro / Enterprise.  
- **Trials**: Configurable per client (days).  
- **Payment gateway**: Stripe (can be toggled on/off).  
- **Usage-based billing**: per invoice after thresholds.  
- **Premium AI packs**: GL coding, fraud detection, workflow Copilot.  
- **Vendor/Supplier monetization**: early pay discounts, compliance scoring.  
- **Marketplace**: paid connectors, third-party extensions.  
- **Analytics Packs**: premium dashboards, Data Lake exports.  
- **Professional services**: onboarding, training, 24/7 premium support.  

---

## 4. Differentiators / Add-On Value
- AI Copilot for financial queries and explanations.  
- Workflow heatmaps and productivity nudges.  
- Multi-currency + tax compliance packs (VAT/GST).  
- Supplier rating + duplicate detection.  
- Immutable ledger & audit sandbox.  
- White-label mode for MSPs.  
- Public API + plugin SDK.  

---

## 5. Testing & Quality Strategy
- **Golden dataset of invoices** (50+ varied layouts).  
- **OCR regression tests**: enforce accuracy thresholds (98% totals, 95% supplier).  
- **Contract tests for ERP adapters**: ensure standard response & idempotency.  
- **Workflow simulations**: multi-approver chains, delegation.  
- **Load & resilience tests**: simulate 1000 invoices/minute, ERP downtime.  
- **Security tests**: SAST, OWASP Top 10.  
- **UAT scenarios**: trial expiry, multi-ERP posting, mobile offline approvals.  

---

## 6. Roadmap & Phases
- **Phase 1 (Pilot)**: GP integration, invoice OCR, approvals, Pro tier subscription.  
- **Phase 2 (Expansion)**: D365 BC, Sage, QuickBooks, Xero adapters. Marketplace beta.  
- **Phase 3 (Global)**: Compliance packs (EU, US, SA). Vendor portal monetization. AI Copilot V2.  
- **Phase 4 (Ecosystem)**: Third-party extensions, payments innovations, white-label SaaS.  

---

## 7. Developer Instructions for Cursor/IDE
- Always generate **full files**, not fragments.  
- Always generate **tests with every feature**.  
- For each phase:  
  - Step 1 → Write failing tests.  
  - Step 2 → Implement production code.  
  - Step 3 → Run tests & output results.  
  - Step 4 → Propose fixes if failing.  
- Use `BUILD_SCRIPT.md` for phase-by-phase execution, with CI/CD, test harness, and rollback instructions.  
- Follow TDD, CI gating, observability, and golden test data enforcement.  

---

## 8. Enterprise-Grade Non-Functional Requirements
- **Scalability**: horizontal scaling via containers & queue workers.  
- **Resilience**: retries, dead-letter queues, circuit breakers for ERP calls.  
- **Observability**: OpenTelemetry, metrics (OCR accuracy, posting success), Sentry integration.  
- **Idempotency**: duplicate invoice postings must not create duplicates.  
- **Security**: SSO (SAML/OIDC), SCIM for user provisioning, data encryption at rest & in transit.  
- **Canary deploys** + rollback automation.  

---

## 9. Final Definition of Done (DoD)
- ✅ Feature code + migrations.  
- ✅ Unit, integration, E2E tests ≥ 85% coverage.  
- ✅ Golden dataset regression green.  
- ✅ Contract tests for adapters green.  
- ✅ Security & compliance scans pass.  
- ✅ Updated OpenAPI schema + docs.  
- ✅ CI/CD pipeline green with deploy preview.  
- ✅ Canary rollout successful with monitoring.  

---

This **Master Prompt Doc** + **BUILD_SCRIPT.md** form the complete playbook to build the application.  
Paste into Cursor system context and execute **phase by phase** until complete.  
