# 🌿 Sacred QA Studio — October Sprint 2 (Week of Oct 7–13, 2025)

**Sprint Theme:** From Stability to Structure  
**CI Baseline:** ✅ Sacred QA CI – Full Gates (v0.3.1-lineage-complete)  
**Duration:** 7 days (Mon–Sun)

---

## 🧩 Track A — Platform Engineering

**Goal:** Refactor MVP into maintainable, testable architecture.

| Priority | Task | Description | Status |
|-----------|------|--------------|--------|
| 🔥 | ORM Refactor | Replace raw SQL with SQLAlchemy models for `sacred_contacts`, `qa_logs`, and `request_lineage` | [ ] |
| 🔥 | Dependency Injection | Use FastAPI `Depends()` for db + agent instantiation | [ ] |
| ⚙️ | Add `pytest` suite | Unit + integration tests for `/health`, `/sankalpa`, and lineage tree | [ ] |
| ⚙️ | APScheduler Integration | Schedule daily health check + lineage cleanup | [ ] |
| ⚙️ | API Versioning | Introduce `/api/v1/` routes | [ ] |
| 🧠 | ORM Migration Commit | Tag release `v0.4.0-orm-stabilized` | [ ] |

**Milestone Output:**  
All CI gates + tests pass in <6 minutes under `Full Gates + Tests` pipeline.

---

## 💼 Track B — Outreach Activation

**Goal:** Convert awareness → booked “Micro-Audits” via calibrated content.

| Priority | Task | Description | Status |
|-----------|------|--------------|--------|
| 🔥 | LinkedIn Post #1 | Publish “2 Bugs in AI Products for Indian Users” (Mon 9 AM IST) | [ ] |
| 🔥 | Email Batch A | Send 10 “Quick QA Win” emails (Mon 8 AM IST) | [ ] |
| 🔥 | Email Batch B | Send 10 “Edge Cases in AI Testing” emails (Mon 3 PM IST) | [ ] |
| ⚙️ | LinkedIn Post #2 | Follow-up: “7 Cultural Patterns AI Tests Miss” (Wed 9 AM IST) | [ ] |
| ⚙️ | Outreach Metrics Log | Track opens/replies in `platform-outreach/tracking/prospects.csv` | [ ] |
| 🧭 | Reflection Audit | End-of-week review: response % + next copy iteration | [ ] |

**Milestone Output:**  
≥ 20 outreach messages sent, ≥ 2 responses, ≥ 1 micro-audit booking.

---

## 🔗 Track C — Integration Bridge (Optional Prep)

**Goal:** Begin connecting outreach → QA logs for traceable marketing events.

| Priority | Task | Description | Status |
|-----------|------|--------------|--------|
| ⚙️ | Create `integration/` folder | Shared environment and bridge code | [ ] |
| ⚙️ | `.env.shared` scaffold | Include `DATABASE_URL`, `CAL_COM_API_KEY`, `SMTP_HOST` | [ ] |
| ⚙️ | API Bridge Script | `api_bridge.py` for logging outreach → `/sankalpa` | [ ] |
| 🧠 | Tag release | `v0.4.1-integration-ready` | [ ] |

**Milestone Output:**  
Outreach scripts can log events to QA Studio via API.

---

## 🧘‍♂️ Daily Focus Timeline

| Day | Focus | Deliverable |
|-----|--------|--------------|
| **Mon (Oct 7)** | Launch outreach (Post #1 + Email A/B) | Live campaign |
| **Tue (Oct 8)** | ORM migration for contacts + logs | PR: `feature/orm-refactor` |
| **Wed (Oct 9)** | LinkedIn Post #2 + test scaffolding | PR: `feature/pytest-suite` |
| **Thu (Oct 10)** | APScheduler setup + cron validation | PR: `feature/apscheduler` |
| **Fri (Oct 11)** | CI Full Gates + Tests pass | Merge to main |
| **Sat (Oct 12)** | Outreach metrics analysis | `metrics_week2.md` |
| **Sun (Oct 13)** | Optional integration bridge setup | `integration/api_bridge.py` |

---

## 🧾 Commit & Tag Milestones

```bash
# Milestone 1 – ORM Stabilization
git tag -a v0.4.0-orm-stabilized -m "ORM migration & DI complete"

# Milestone 2 – Outreach Week 2 Complete
git tag -a v0.4.0-outreach-wave2 -m "20 emails sent, 2 replies logged"

# Milestone 3 – Integration Ready
git tag -a v0.4.1-integration-ready -m "Shared env + API bridge setup"
