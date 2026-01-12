# CRM Project Timeline Path

Five sequential phases mark project progress milestones.

---

## Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12+ | Runtime |
| Django | 5.0.x | Web framework |
| Gunicorn | 21.2+ | WSGI server |
| django-environ | 0.11+ | Environment configuration |
| django-allauth | 0.63+ | Authentication (Google, Microsoft OAuth) |
| django-htmx | 1.17+ | HTMX integration |
| django-storages | 1.14+ | Cloud storage abstraction |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| HTMX | Latest | Dynamic HTML without JavaScript frameworks |
| Alpine.js | Latest | Lightweight reactivity |
| Tailwind CSS | 3.4+ | Utility-first styling |

### Database
| Environment | Database | Rationale |
|-------------|----------|-----------|
| Development | SQLite | Zero setup, fast iteration |
| Production | PostgreSQL 15+ (Cloud SQL) | ACID compliance, scalability, GCP native |

### Infrastructure (GCP)
| Service | Purpose |
|---------|---------|
| Cloud Run | Container hosting (serverless) |
| Cloud SQL | Managed PostgreSQL |
| Cloud Storage | Static files & media uploads |
| Cloud Tasks | Async job processing |
| Secret Manager | Credentials management |
| Cloud Build | CI/CD pipeline |

### Development Tools
| Tool | Purpose |
|------|---------|
| pytest | Testing framework |
| pytest-cov | Code coverage |
| factory-boy | Test fixtures |
| black | Code formatting |
| flake8 | Linting |
| isort | Import sorting |

---

## Development Methodology

### Sprint Structure: 2-Week Sprints

We will follow **Scrum with Kanban elements** for flexibility.

```
Week 1: Build
├── Day 1-2: Sprint planning + development start
├── Day 3-5: Core feature development
└── Daily: 15-min standups

Week 2: Refine & Ship
├── Day 6-8: Feature completion + testing
├── Day 9: Code review + QA
└── Day 10: Sprint demo + retrospective
```

### Sprint Ceremonies
| Ceremony | Duration | Frequency |
|----------|----------|-----------|
| Sprint Planning | 2 hours | Start of sprint |
| Daily Standup | 15 min | Daily |
| Sprint Review/Demo | 1 hour | End of sprint |
| Retrospective | 30 min | End of sprint |
| Backlog Refinement | 1 hour | Mid-sprint |

### Definition of Done
- [ ] Code complete and follows style guide
- [ ] Unit tests written (80%+ coverage for new code)
- [ ] Code review approved
- [ ] No critical/high bugs
- [ ] Documentation updated (if applicable)
- [ ] Tested in staging environment

---

## Quality Gates

### Code Quality Standards
- **Black** formatting enforced (line length: 88)
- **Flake8** linting with zero errors
- **isort** import ordering
- Test coverage minimum: 80%
- No security vulnerabilities (OWASP Top 10)

### Git Workflow
```
main (protected)
  └── develop
        ├── feature/CRM-xxx-feature-name
        ├── bugfix/CRM-xxx-bug-description
        └── hotfix/CRM-xxx-critical-fix
```

### Pull Request Requirements
1. Descriptive title with ticket reference
2. At least 1 code review approval
3. All CI checks passing
4. No merge conflicts
5. Linked to relevant issue/ticket

---

## Phase 1: Define Vision

Set clear project objectives and long-term outcomes.

### Objectives
- [x] Establish project goals and success criteria
- [x] Define target users and use cases
- [x] Align stakeholders on priorities
- [x] Select tech stack and architecture

### Deliverables
- Project charter document
- User personas defined
- High-level requirements gathered

---

## Phase 2: Outline Scope

Determine deliverables, tasks, and resource allocation.

### Sprint 1: Foundation (Current)
- [x] Project scaffolding
- [x] User authentication system
- [x] Check-in/check-out tracking
- [x] Django Admin setup
- [x] Test infrastructure

### Sprint 2: Pipeline Core
- [ ] Deal model with 9 pipeline stages
- [ ] Pipeline board view (Kanban)
- [ ] Deal CRUD operations
- [ ] Stage transition logic

### Sprint 3: Client Management
- [ ] Client model and views
- [ ] Client-Deal relationships
- [ ] Basic client dashboard
- [ ] File attachments

---

## Phase 3: Build Increment

Develop new features in small, manageable and efficient stages.

### Sprint 4: Communications
- [ ] Call logging
- [ ] Email integration (Gmail OAuth)
- [ ] Email templates (macros)
- [ ] Activity feed

### Sprint 5: Scheduling & Invoicing
- [ ] Site visit scheduling
- [ ] Invoice management
- [ ] Payment tracking
- [ ] Calendar integration

### Sprint 6: Polish & Integration
- [ ] UI/UX refinements
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] Integration testing

---

## Phase 4: Test Results

Validate deliverables against quality benchmarks and requirements.

### Sprint 7: QA & Hardening
- [ ] End-to-end testing
- [ ] Security audit
- [ ] Performance testing
- [ ] User acceptance testing (UAT)
- [ ] Bug fixes from UAT

### Quality Checklist
- [ ] All critical user flows tested
- [ ] Load testing completed (target: 100 concurrent users)
- [ ] Security scan passed
- [ ] Accessibility review (WCAG 2.1 AA)
- [ ] Cross-browser testing

---

## Phase 5: Release Product

Deliver the final version for immediate use or for valuable customer feedback.

### Sprint 8: Deployment
- [ ] Production infrastructure setup
- [ ] SSL/Domain configuration
- [ ] Monitoring & alerting (Sentry)
- [ ] Backup procedures verified
- [ ] Go-live checklist complete

### Post-Launch
- [ ] User training sessions
- [ ] Documentation finalized
- [ ] Feedback collection process
- [ ] Support procedures established

---

# Deal Cycle (Business Development)

The core workflow for managing deals through the CRM:

| Stage | Description | Owner |
|-------|-------------|-------|
| **01. Screening** | Pre-qualifying deals and uploading to the CRM | Business Development |
| **02. Estimating** | Estimators get the files and prepare a quote | Estimators |
| **03. Nurture** | Build relationship and do follow-up | Business Development |
| **04. Negotiation** | Negotiate until client signs the contract | Business Development |
| **05. Project Turnover** | Once contract is signed, turn-over to project/operations | Operations |

---

# Core Focus Areas

### 01. Simple Client Dashboard
Client dashboard should have all the necessary buttons/features for project management and progress tracking.

### 02. Analytics/Reporting
Robust reporting and analytics structure and view.

### 03. Integration and Automation
Automation and AI-geared system.

---

# Essential Elements (Monday)

### 01. User Account
- System that requires log in from staff
- Serves as check-in, check-out tracking

### 02. Pipeline Structure
Duplicate pipeline structure from current CRM:
1. New Request
2. Engaged
3. Estimate in Progress
4. Estimate Sent
5. Follow-up
6. Negotiation
7. Closed Won
8. Closed Lost (with Sub Reason)
9. Declined to Bid (with Sub Reason)

### 03. Client Dashboard

**Important Buttons:**
- Call
- Email (enable macro templates)
- Site-visit schedule
- Invoice/Payments
- Attachments

**Features:**
- User logs
- Call log
- Email log
- Activity log

---

# Risk Management

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep | High | Strict sprint boundaries, change request process |
| OAuth integration delays | Medium | Early spike, fallback to manual email logging |
| Performance issues | Medium | Regular load testing, query optimization |
| Team availability | Medium | Cross-training, documentation |

---

# Success Metrics

| Metric | Target |
|--------|--------|
| Sprint velocity | Stable after Sprint 3 |
| Bug escape rate | < 5% to production |
| Test coverage | > 80% |
| Page load time | < 2 seconds |
| User adoption | 90% within 2 weeks of launch |

---

# Gantt Chart

## Project Timeline (16 Weeks / 8 Sprints)

| Phase | Sprint | W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 | W9 | W10 | W11 | W12 | W13 | W14 | W15 | W16 |
|-------|--------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **PHASE 1: DEFINE VISION** |
| Define Vision | - | ■ | | | | | | | | | | | | | | | |
| **PHASE 2: OUTLINE SCOPE** |
| Foundation | S1 | | ■ | ■ | | | | | | | | | | | | | |
| Pipeline Core | S2 | | | | ■ | ■ | | | | | | | | | | | |
| Client Mgmt | S3 | | | | | | ■ | ■ | | | | | | | | | |
| **PHASE 3: BUILD INCREMENT** |
| Communications | S4 | | | | | | | | ■ | ■ | | | | | | | |
| Scheduling | S5 | | | | | | | | | | ■ | ■ | | | | | |
| Polish | S6 | | | | | | | | | | | | ■ | ■ | | | |
| **PHASE 4: TEST RESULTS** |
| QA & Hardening | S7 | | | | | | | | | | | | | | ■ | ■ | |
| **PHASE 5: RELEASE** |
| Deployment | S8 | | | | | | | | | | | | | | | | ■ |

**Legend:** ■ = Active Sprint

## Detailed Sprint Calendar

| Sprint | Phase | Focus Area | Weeks | Key Deliverables |
|--------|-------|------------|-------|------------------|
| - | Phase 1 | Define Vision | 1 | Requirements, tech decisions |
| S1 | Phase 2 | Foundation | 2-3 | Auth, check-in/out, admin |
| S2 | Phase 2 | Pipeline Core | 4-5 | Deal model, Kanban board |
| S3 | Phase 2 | Client Management | 6-7 | Client dashboard, attachments |
| S4 | Phase 3 | Communications | 8-9 | Email integration, call logs |
| S5 | Phase 3 | Scheduling & Invoicing | 10-11 | Site visits, payments |
| S6 | Phase 3 | Polish & Integration | 12-13 | UI refinements, optimization |
| S7 | Phase 4 | QA & Hardening | 14-15 | Testing, security audit, UAT |
| S8 | Phase 5 | Deployment | 16 | Go-live, training |

## Milestone Dates (Example Starting Jan 13, 2025)

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Project Kickoff | Jan 13 | Complete |
| Foundation Complete | Jan 24 | In Progress |
| Pipeline MVP | Feb 7 | Pending |
| Client Dashboard Ready | Feb 21 | Pending |
| Communications Live | Mar 7 | Pending |
| Feature Complete | Mar 21 | Pending |
| QA Sign-off | Apr 4 | Pending |
| Production Launch | Apr 11 | Pending |

---

# Cost Estimates

## Project Parameters

| Parameter | Value |
|-----------|-------|
| Team Size | 1 Developer (AI-assisted with Claude Code) |
| Target Users | 10-25 (fixed, no growth) |
| Development Duration | 16 weeks (4 months) |
| Developer Salary | $3,000 USD/month |

---

## Development Costs

### Team Structure
| Role | Allocation | Monthly Cost |
|------|------------|--------------|
| Full-Stack Developer | 1 FTE | $3,000 |
| Claude Code Max | Subscription | $100-200 |
| **Dev Monthly Total** | | **$3,100-3,200** |

### Development Phase Total (16 weeks / 4 months)
| Item | Cost |
|------|------|
| Developer Salary (4 months) | $12,000 |
| Claude Code Max (4 months) | $400-800 |
| **Development Total** | **$12,400-12,800** |

---

## GCP Infrastructure Costs

### Development/Staging Environment
| Service | Specs | Monthly Cost |
|---------|-------|--------------|
| Cloud Run | 1 instance, minimal | $0-5 |
| Cloud SQL | db-f1-micro, 10GB | $10-15 |
| Cloud Storage | 5GB | $0.10 |
| Cloud Build | 120 min/day free | $0 |
| **Dev Total** | | **~$15/month** |

### Production Environment (10-25 users)
| Service | Specs | Monthly Cost |
|---------|-------|--------------|
| Cloud Run | 1 vCPU, 512MB RAM, auto-scale 0-2 | $15-30 |
| Cloud SQL | db-g1-small, 20GB SSD | $35-50 |
| Cloud Storage | 25GB + egress | $3-8 |
| Cloud Tasks | 500K tasks/month | $0.20 |
| Secret Manager | 10 secrets | $0.60 |
| **Prod Total** | | **~$55-90/month** |

*Note: 10-25 users with moderate usage doesn't require high-availability or large instances.*

---

## Third-Party Services

| Service | Purpose | Monthly Cost |
|---------|---------|--------------|
| Sentry | Error tracking | $0 (free tier) |
| Domain | Custom domain | ~$1 |
| SSL | Via Cloud Run (free) | $0 |
| **Third-Party Total** | | **~$1/month** |

---

## Total Cost Summary

### One-Time Development Costs
| Item | Cost |
|------|------|
| Developer Salary (4 months) | $12,000 |
| Claude Code Max (4 months) | $600 |
| Domain Registration (1 year) | $15 |
| **One-Time Total** | **~$12,615** |

### Monthly Operating Costs (Post-Launch)
| Item | Monthly Cost |
|------|--------------|
| GCP Production | $70 |
| Third-Party | $1 |
| **Monthly Total** | **~$71/month** |

### Annual Operating Costs (Post-Launch)
| Item | Annual Cost |
|------|-------------|
| GCP Production (12 months) | $840 |
| Domain Renewal | $15 |
| Third-Party | $12 |
| **Annual Total** | **~$867/year** |

---

## Complete Cost Breakdown

### Year 1 (Development + Operations)
| Phase | Duration | Cost |
|-------|----------|------|
| Development | Months 1-4 | $12,615 |
| GCP during dev | Months 1-4 | $60 |
| Production | Months 5-12 | $568 |
| **Year 1 Total** | | **~$13,243** |

### Year 2+ (Operations Only)
| Item | Annual Cost |
|------|-------------|
| GCP Production | $840 |
| Domain + misc | $27 |
| **Year 2+ Total** | **~$867/year** |

---

## Cost Optimization Tips

1. **Use Cloud Run min instances = 0** - scales to zero when idle
2. **db-g1-small is sufficient** for 10-25 users with moderate load
3. **Use GCP Free Tier** during development:
   - Cloud Run: 2M requests/month free
   - Cloud Build: 120 build-min/day free
   - Cloud Storage: 5GB free
4. **Set budget alerts** at $50, $75, $100 thresholds
5. **Consider 1-year committed use** for Cloud SQL (up to 25% savings)

---

## ROI Comparison

| Metric | This CRM | SaaS Alternative |
|--------|----------|------------------|
| Development Cost | $12,615 | $0 |
| Monthly (25 users) | $71 | $500-1,250* |
| Year 1 Total | $13,243 | $6,000-15,000 |
| Year 2 Total | $867 | $6,000-15,000 |
| **Break-even** | | **~1-2 years** |

*SaaS CRM pricing typically $20-50/user/month for comparable features*
