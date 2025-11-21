---
id: 3
title: Plan Geospatial AI Interface
stage: plan
date: 2025-11-22
surface: agent
model: gemini-pro
feature: 001-geospatial-ai-interface
branch: 001-geospatial-ai-interface
user: User
command: /sp.plan
labels: ["plan"]
links:
  spec: ./specs/001-geospatial-ai-interface/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-geospatial-ai-interface/plan.md
  - specs/001-geospatial-ai-interface/research.md
  - specs/001-geospatial-ai-interface/data-model.md
  - specs/001-geospatial-ai-interface/contracts/openapi.yaml
  - specs/001-geospatial-ai-interface/quickstart.md
tests:

---

## Prompt

/sp.plan 1. Product Overview

GeoMind AI is an AI-powered interface that allows geoscientists, data managers, and reservoir engineers to interact with Landmark OpenWorks (Oracle RDBMS) using plain-English queries. The system interprets user input, converts it into validated SQL, executes queries safely, and presents formatted results.
GeoMind AI acts as an external intelligence layer, requiring no modification to OpenWorks software, only access to its Oracle database schema.

2. Purpose

The purpose of GeoMind AI is to:

Provide a natural-language interface to OpenWorks.

Simplify the complexity of querying, updating, and managing subsurface data.

Ensure safe operations, auditability, and compliance for all database actions.

Accelerate workflows involving wells, logs, seismic metadata, markers, and interpretation datasets.

Serve as an enterprise-scale AI assistant bridging geoscience expertise and automation.

3. Scope
3.1 Included Functional Domains
3.1.1 Natural Language Understanding

Interpret plain-English questions and commands.

Detect user intent (retrieve, update, insert, edit, metadata).

Translate geoscience terminology to OpenWorks schema tables and columns.

Resolve ambiguities via follow-up questions.

3.1.2 Schema-Aware SQL Generation

Generate SQL statements consistent with OpenWorks schema.

Validate SQL against:

Table existence

Column existence

Allowed joins

Permission model

Reject unsafe or high-risk queries.

3.1.3 Oracle Database Access

Execute read operations across accessible OpenWorks schemas.

Perform controlled write/update operations after explicit user approval.

Use parameterized queries to avoid SQL injection.

Log every SQL operation with timestamp and user ID.

3.1.4 User Interface

Chat-based conversational interface.

Tabular result view with export options (CSV/Excel).

SQL preview with reasoning and explanations.

Dark mode for geoscience workflow environments.

3.1.5 Governance & Safety

Role-based access control (RBAC).

Multi-step approval for sensitive writes.

Full audit trail with rollback capability.

Safety guardrails to prevent:

Schema modifications

Invalid writes

Unauthorized operations

4. Functional Requirements
4.1 Query Understanding

Accept free-text English input.

Identify tables, constraints, filters, and metrics requested.

Ask clarifying questions when context is missing.

Enforce confirmation for edit requests.

4.2 SQL Generation & Validation

Generate SQL aligned with the OpenWorks schema.

Validate using:

Schema introspection engine

Permission model

Safety rules

Reject ambiguous queries or request clarification.

4.3 Execution Logic

Execute SELECT queries immediately if safe.

Require confirmation for UPDATE/INSERT operations.

Admin approval for sensitive updates (optional).

Cache results for repeated queries.

4.4 Audit & Traceability

Each operation logs:

User identity

Timestamp

SQL text

Affected tables and rows

Execution duration

4.5 User Output

System returns:

Well-formatted responses

Full data tables or summaries for large datasets

SQL explanations

Secure, descriptive error messages

5. Non-Functional Requirements
5.1 Performance

Support 1000+ concurrent chat sessions.

Sub-2 second response time for cached/optimized queries.

Pagination optimized for large datasets.

5.2 Scalability

Stateless microservices.

Horizontal scaling via Kubernetes.

Independent scaling for:

AI inference

DB Gateway

UI backend

5.3 Reliability

Automatic retry for transient Oracle errors.

Graceful failover for AI model unavailability.

Zero data loss guarantee.

5.4 Security

Enforced authentication (OIDC/SSO).

Oracle credentials stored in a secure vault.

No direct SQL input allowed from users.

All SQL validated via AI + rule engine.

5.5 Compliance

Full audit logs per regulatory policy.

Configurable role permissions aligned with subsurface data governance.

6. System Architecture
6.1 Core Components

AI Orchestrator

Intent classification, SQL generation, query reasoning

Schema/Ontology Engine

Stores OpenWorks schema

Maps synonyms (e.g., "MD" → "MEASURED_DEPTH")

Validates table/column existence

SQL Safety Validator

Detects unsafe operations

Enforces RBAC

Blocks unapproved statements

Oracle Data Gateway

Executes validated SQL

Handles parameterized queries

Logs results

Chat Application Backend

Session management

Tokenization

Result caching

Frontend Web App

AI chat interface

Tabs for schema, history, exports

SQL preview window

7. Dependencies
7.1 Technology Stack

Frontend: Next.js, React, Tailwind

Backend: FastAPI or Node.js (NestJS)

AI/NLP: Python, LangChain / LlamaIndex

Database: Oracle 19c (OpenWorks)

Vector Storage: pgvector or Chroma

Infra: Docker, Kubernetes

Auth: Auth0 / Azure AD / Keycloak

Logging & Monitoring: ELK / Loki / Grafana

8. User Experience (UX) Principles
8.1 Conversational Simplicity

Avoid overwhelming users

Offer hints, suggestions, and guidance

8.2 Transparency

Always show SQL and reasoning

8.3 Speed

Fast UI interactions

Preload common schema terms

8.4 Professional Communication

Technical, concise, and objective

Explain uncertainties when needed

9. Success Metrics
9.1 Technical KPIs

SQL generation accuracy > 95%

Error rate < 1%

Query latency < 2s

9.2 User Adoption KPIs

Weekly active users

Number of queries executed

Reduction in manual SQL writing

9.3 Business KPIs

Time saved per geoscientist per week

Fewer data quality errors

Faster OpenWorks data management workflows

10. Evolution Roadmap
Phase 1 – MVP

Chat → SQL → Oracle

Read-only queries

Ontology & schema mapping

SQL preview

Basic UI

Phase 2 – Full CRUD & Governance

Update/insert workflows

Role-based access controls

Full auditing & rollback

Data quality assistant

Phase 3 – Advanced AI

Well log QC agent

Seismic metadata intelligence

Cross-platform integration (Petrel, OSDU)

Predictive query engine & caching

## Response snapshot

I have completed the implementation planning phase for the GeoMind AI Core feature. The following artifacts have been created:

- `specs/001-geospatial-ai-interface/plan.md`: The high-level implementation plan.
- `specs/001-geospatial-ai-interface/research.md`: Documentation of technology choices.
- `specs/001-geospatial-ai-interface/data-model.md`: The conceptual data model.
- `specs/001-geospatial-ai-interface/contracts/openapi.yaml`: The API contract.
- `specs/001-geospatial-ai-interface/quickstart.md`: A quickstart guide for developers.

The agent context has also been updated. The feature is now ready for the task generation phase (`/sp.tasks`).

## Outcome

- ✅ Impact: The implementation plan for the GeoMind AI Core feature has been created.
- 🧪 Tests: No tests were run.
- 📁 Files: 
  - `specs/001-geospatial-ai-interface/plan.md` created.
  - `specs/001-geospatial-ai-interface/research.md` created.
  - `specs/001-geospatial-ai-interface/data-model.md` created.
  - `specs/001-geospatial-ai-interface/contracts/openapi.yaml` created.
  - `specs/001-geospatial-ai-interface/quickstart.md` created.
  - `history/prompts/001-geospatial-ai-interface/3-plan-geospatial-ai-interface.plan.prompt.md` was created.
- 🔁 Next prompts: The user can now proceed with task generation (`/sp.tasks`).
- 🧠 Reflection: The manual creation of the plan and PHR files was successful.

## Evaluation notes (flywheel)

- Failure modes observed: `setup-plan.sh` and `create-phr.sh` scripts did not produce the expected output, requiring manual file creation.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
