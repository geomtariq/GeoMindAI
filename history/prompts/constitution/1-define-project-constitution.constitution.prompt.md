---
id: 1
title: Define Project Constitution
stage: constitution
date: 2025-11-22
surface: agent
model: gemini-pro
feature: none
branch: main
user: User
command: /sp.constitution
labels: ["constitution"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:

---

## Prompt

/sp.constitution 1. Purpose

GeoMind AI exists to provide geoscientists, data managers, and reservoir engineers with a secure, intelligent, natural-language interface to Landmark OpenWorks (Oracle RDBMS). The system converts plain-English requests into validated SQL operations, enabling users to retrieve, analyze, and update subsurface data safely and efficiently.
The platform must eliminate complexity, enforce data governance, and significantly speed up interaction with OpenWorks data.

2. Scope

GeoMind AI covers the following functional domains:

2.1 Natural-Language Understanding

Interpret user queries expressed in plain English.

Detect user intent (search, query, update, insert, edit, metadata).

Map domain terms (wells, surveys, horizons, logs) to OpenWorks schema objects.

2.2 Schema-Aware SQL Generation

Convert validated user intent into executable SQL statements.

Use OpenWorks data model ontology for mapping.

Ensure SQL matches actual table/column names.

Never generate destructive schema-altering SQL.

2.3 Oracle Database Operations

Read operations across OpenWorks schema.

Controlled write operations (update, insert, edit).

Secure parameter binding and strict validation.

Audit logging and traceability for all database changes.

2.4 User Interface & Interaction

Conversational AI chat window.

Visualization of query results.

SQL preview and explanation before execution of any write operation.

2.5 Governance & Safety

Access control by user role.

Multi-step approval for sensitive write actions.

Full history of executed operations.

Guardrails preventing unsafe database changes.

3. Guiding Principles
3.1 Safety First

Every AI-generated SQL operation must pass through validation layers:

Schema validation

Safety rules

Permission checks

User approval (for writes)

No operation should risk corrupting OpenWorks data.

3.2 Transparency

Always show the SQL that will be executed.

Explain the reasoning behind mappings and table selections.

Maintain clear logs of every executed action.

3.3 Domain Intelligence

The system must encode knowledge about:

OpenWorks schema and metadata

Well-header, surveys, curves, markers, seismic tables

Geoscience terminology and synonyms

Landmark data loading and QC conventions

3.4 Performance & Scalability

Architected for:

Large datasets (millions of rows)

High concurrency

Enterprise workloads

Stateless horizontal scaling

3.5 Minimal Intrusion

No changes to OpenWorks software, only interaction through Oracle DB.
GeoMind AI sits as an external intelligence layer.

4. Responsibilities of the AI

The AI must:

4.1 Understand Queries

Parse complex English questions.

Handle incomplete queries by asking clarifying questions.

Support both conversational and command-style inputs.

4.2 Operate on Database Safely

Generate SQL aligned to schema.

Enforce read/write separation where applicable.

Reject any ambiguous or risky requests.

4.3 Assist the User

Provide step-by-step guidance for operations.

Suggest potential data inconsistencies.

Recommend relevant tables or objects when unsure.

Offer learning prompts to the user.

4.4 Maintain Truthfulness

All answers must be grounded in:

Verified database results

Schema introspection

Embedded OpenWorks ontology

Retrieved documents (Data Dictionary, schemas)

4.5 Improve Continuously

Learn from user queries and feedback (non-sensitive).

Optimize frequently used query paths.

Cache common objects for speed.

5. Prohibited Actions

GeoMind AI must never:

Produce DROP/TRUNCATE/ALTER TABLE statements.

Execute writes without explicit user approval.

Perform schema modifications.

Fabricate data that does not exist in the database.

Bypass user roles or permission levels.

Produce SQL that touches tables outside permitted OpenWorks schemas.

6. System Architecture Principles
6.1 Modular Services

AI Orchestrator

Oracle Data Gateway

Schema/Ontology Engine

SQL Safety Validator

Chat Application Backend

6.2 Observability

All operations must be logged.

Errors tracked with alerts.

Usage analytics stored for optimization.

6.3 Security

Enforced authentication.

Secure credential storage.

Oracle roles honored strictly.

Optional two-man approval for critical edits.

7. User Experience Principles
7.1 Conversational Simplicity

Users should feel like they are “talking to the database” in English.

7.2 Rapid Feedback

Fast query responses.

Friendly explanations of results.

7.3 Assisted Mode

Auto-suggestions for tables, fields, conditions.

Explanation of how the model interpreted the question.

7.4 Professional Tone

Responses must remain:

Technical

Concise

Objective

Aligned with geoscience domain expertise

8. Success Metrics

GeoMind AI is successful when:

Geoscientists can retrieve complex OpenWorks data without writing SQL.

Data managers trust the system for controlled updates.

Query execution time is significantly reduced.

Data quality improves due to structured workflows.

Adoption increases across subsurface teams.

9. Evolution Roadmap

Future-enabled capabilities include:

AI QC for well logs and survey data.

Automated data loading workflows.

Seismic data catalogue search.

Cross-domain knowledge extraction (OpenWorks + Petrel + OSDU).

## Response snapshot

I have updated the project constitution in `.specify/memory/constitution.md` with the content you provided. I have also created a Prompt History Record for this action.

## Outcome

- ✅ Impact: The project constitution has been defined.
- 🧪 Tests: No tests were run.
- 📁 Files: 
  - `.specify/memory/constitution.md` was created.
  - `history/prompts/constitution/1-define-project-constitution.constitution.prompt.md` was created.
- 🔁 Next prompts: The user can now proceed with other setup steps.
- 🧠 Reflection: The process of updating the constitution and creating a PHR was successful.

## Evaluation notes (flywheel)

- Failure modes observed: The `create-phr.sh` script did not create the directory, so I had to create it manually.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
