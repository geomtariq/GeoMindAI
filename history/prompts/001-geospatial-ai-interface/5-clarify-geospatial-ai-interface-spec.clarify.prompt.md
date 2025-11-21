---
id: 5
title: Clarify Geospatial AI Interface Spec
stage: clarify
date: 2025-11-22
surface: agent
model: gemini-pro
feature: 001-geospatial-ai-interface
branch: 001-geospatial-ai-interface
user: User
command: /sp.clarify 1. Product Overview GeoMind AI is an AI-driven interface that enables geoscientists, data managers, and subsurface engineers to interact with Landmark OpenWorks (Oracle RDBMS) using natural language. The system interprets user queries, converts them into validated SQL, performs secure read/write operations, and returns formatted results. The system is designed as an external intelligence layer that requires no modification to OpenWorks software, only access to its Oracle database schema. 2. Purpose The purpose of GeoMind AI is to: Provide a plain-English query interface to OpenWorks. Reduce the complexity of querying, updating, and managing subsurface data. Ensure complete safety, auditability, and compliance during database operations. Accelerate workflows related to wells, logs, seismic metadata, markers, and interpretation datasets. Serve as an enterprise-scale assistant bridging geoscience expertise with AI automation. 3. Scope 3.1 Included Functional Domains 3.1.1 Natural Language Understanding Interpret plain-English questions and commands. Detect user intent (retrieve, update, insert, edit, metadata). Translate geoscience terminology into OpenWorks schema tables and columns. Resolve ambiguities through follow-up questions. 3.1.2 Schema-Aware SQL Generation Generate contextually correct SQL based on OpenWorks schema. Validate generated SQL against: Table existence Field existence Allowed joins Permission model Reject unsafe or high-risk SQL operations. 3.1.3 Oracle Database Access Execute read operations across all accessible OpenWorks schemas. Perform controlled write/update operations after user approval. Use parameter binding to avoid SQL injection. Log each executed SQL query with timestamp and user ID. 3.1.4 User Interface Chat-based interface for natural interaction. Tabular view for query results. Query preview (SQL + reasoning). Result export (CSV/Excel). Dark mode for geoscientist workflow environments. 3.1.5 Governance &... [truncated]
labels: ["clarification"]
links:
  spec: ./specs/001-geospatial-ai-interface/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-geospatial-ai-interface/spec.md
tests:

---

## Prompt

1. Product Overview GeoMind AI is an AI-driven interface that enables geoscientists, data managers, and subsurface engineers to interact with Landmark OpenWorks (Oracle RDBMS) using natural language. The system interprets user queries, converts them into validated SQL, performs secure read/write operations, and returns formatted results. The system is designed as an external intelligence layer that requires no modification to OpenWorks software, only access to its Oracle database schema. 2. Purpose The purpose of GeoMind AI is to: Provide a plain-English query interface to OpenWorks. Reduce the complexity of querying, updating, and managing subsurface data. Ensure complete safety, auditability, and compliance during database operations. Accelerate workflows related to wells, logs, seismic metadata, markers, and interpretation datasets. Serve as an enterprise-scale assistant bridging geoscience expertise with AI automation. 3. Scope 3.1 Included Functional Domains 3.1.1 Natural Language Understanding Interpret plain-English questions and commands. Detect user intent (retrieve, update, insert, edit, metadata). Translate geoscience terminology into OpenWorks schema tables and columns. Resolve ambiguities through follow-up questions. 3.1.2 Schema-Aware SQL Generation Generate contextually correct SQL based on OpenWorks schema. Validate generated SQL against: Table existence Field existence Allowed joins Permission model Reject unsafe or high-risk SQL operations. 3.1.3 Oracle Database Access Execute read operations across all accessible OpenWorks schemas. Perform controlled write/update operations after user approval. Use parameter binding to avoid SQL injection. Log each executed SQL query with timestamp and user ID. 3.1.4 User Interface Chat-based interface for natural interaction. Tabular view for query results. Query preview (SQL + reasoning). Result export (CSV/Excel). Dark mode for geoscientist workflow environments. 3.1.5 Governance &... [truncated]

## Response snapshot

I have asked and answered 5 questions to clarify the GeoMind AI Core feature specification. The `spec.md` file has been updated accordingly, and all critical ambiguities have been resolved.

## Outcome

- ✅ Impact: The feature specification for GeoMind AI Core has been clarified and updated.
- 🧪 Tests: No tests were run.
- 📁 Files: 
  - `specs/001-geospatial-ai-interface/spec.md` was updated.
  - `history/prompts/001-geospatial-ai-interface/5-clarify-geospatial-ai-interface-spec.clarify.prompt.md` was created.
- 🔁 Next prompts: The user can now proceed with implementation.
- 🧠 Reflection: The manual updates due to tool limitations were successfully managed.

## Evaluation notes (flywheel)

- Failure modes observed: `check-prerequisites.sh` and `create-phr.sh` scripts did not produce the expected output, requiring manual file creation.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
