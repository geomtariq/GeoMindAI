# Feature Specification: GeoMind AI Core

**Feature Branch**: `001-geospatial-ai-interface`  
**Created**: 2025-11-22  
**Status**: Draft  
**Input**: User description: "1. Product Overview GeoMind AI is an AI-driven interface that enables geoscientists, data managers, and subsurface engineers to interact with Landmark OpenWorks (Oracle RDBMS) using natural language. The system interprets user queries, converts them into validated SQL, performs secure read/write operations, and returns formatted results. The system is designed as an external intelligence layer that requires no modification to OpenWorks software, only access to its Oracle database schema. 2. Purpose The purpose of GeoMind AI is to: Provide a plain-English query interface to OpenWorks. Reduce the complexity of querying, updating, and managing subsurface data. Ensure complete safety, auditability, and compliance during database operations. Accelerate workflows related to wells, logs, seismic metadata, markers, and interpretation datasets. Serve as an enterprise-scale assistant bridging geoscience expertise with AI automation. 3. Scope 3.1 Included Functional Domains 3.1.1 Natural Language Understanding Interpret plain-English questions and commands. Detect user intent (retrieve, update, insert, edit, metadata). Translate geoscience terminology into OpenWorks schema tables and columns. Resolve ambiguities through follow-up questions. 3.1.2 Schema-Aware SQL Generation Generate contextually correct SQL based on OpenWorks schema. Validate generated SQL against: Table existence Field existence Allowed joins Permission model Reject unsafe or high-risk SQL operations. 3.1.3 Oracle Database Access Execute read operations across all accessible OpenWorks schemas. Perform controlled write/update operations after user approval. Use parameter binding to avoid SQL injection. Log each executed SQL query with timestamp and user ID. 3.1.4 User Interface Chat-based interface for natural interaction. Tabular view for query results. Query preview (SQL + reasoning). Result export (CSV/Excel). Dark mode for geoscientist workflow environments. 3.1.5 Governance & Safety Role-based access control (RBAC). Multi-step approval workflow for sensitive writes. Full audit trail and rollback registry. Safety guardrails to prevent: Schema modifications Invalid writes Unauthorized operations 4. Functional Requirements 4.1 Query Understanding The system must: Accept free-text English input. Determine table(s), constraints, filters, and metrics requested. Identify missing context and ask clarifying questions. Detect when the user requests edits and enforce confirmation. 4.2 SQL Generation & Validation Generate SQL aligned with the Oracle OpenWorks schema. Validate SQL using: Schema introspection engine Permission model Safety rules Reject or request clarification for ambiguous queries. 4.3 Execution Logic Route SELECT queries immediately if safe. Require confirmation before UPDATE/INSERT operations. Require admin approval for sensitive updates (optional). Execute queries against Oracle via secure DB connection. Store results in temporary cache for faster repeated queries. 4.4 Audit & Traceability Each operation must have: User identity Timestamp Structured SQL log text Affected tables and rows Execution duration 4.5 User Output System must return: Well-formatted responses Complete data tables Summaries for large datasets SQL explanation Error messages that are descriptive but secure (no DB leaks) 5. Non-Functional Requirements 5.1 Performance Handle 1000+ concurrent chat sessions. Sub-2 second response time for cached/optimized queries. Optimized pagination for large tables. 5.2 Scalability Stateless microservices. Horizontal scaling via Kubernetes. Independent scaling for: AI inference DB Gateway UI backend 5.3 Reliability Automatic retries for transient Oracle errors. Graceful failover for AI model unavailability. Zero data loss during operations. 5.4 Security Enforced user authentication (OIDC/SSO). Oracle credentials stored in secure vault. No direct SQL entry allowed from user. All SQL must be LLM-and-rule-validated. 5.5 Compliance Full audit logs per company and regulatory policies. Configurable role permissions aligned with subsurface data governance. 6. System Architecture 6.1 Core Components AI Orchestrator Intent classification SQL generation Query reasoning Schema/Ontology Engine Stores OpenWorks schema structure Synonym mapping (e.g., "MD" = "MEASURED_DEPTH") Table and column validation SQL Safety Validator Detects dangerous operations Blocks unapproved statements Enforces RBAC Oracle Data Gateway Executes final validated SQL Handles parameterized queries Logs results Chat Application Backend Session management Tokenization Result caching Frontend Web App AI chat UI Tabs for schema, history, exports SQL preview window 7. Dependencies 7.1 Technology Stack Frontend: Next.js, React, Tailwind Backend: FastAPI or Node.js (NestJS) AI Pipeline: Python, LangChain / LlamaIndex Database: Oracle 19c (OpenWorks) Vector Storage: pgvector or Chroma Infra: Docker, Kubernetes Auth: Auth0 / Azure AD / Keycloak Logging: Elastic Stack / Loki / Grafana 8. User Experience (UX) Principles 8.1 Conversational Simplicity Never overwhelm the user. Offer options, hints, and suggestions. 8.2 Transparency Always show SQL and reasoning. 8.3 Speed Deliver fast UI interactions. Preload common schema terms. 8.4 Professional Communication Use technical but clear responses. Explain uncertainties. 9. Success Metrics 9.1 Technical KPIs SQL accuracy > 95% Error rate < 1% Query latency < 2s 9.2 User Adoption KPIs Weekly active users Number of queries executed Reduction in manual SQL writing 9.3 Business KPIs Time saved per geoscientist per week Fewer data quality errors Faster OpenWorks data management workflows 10. Evolution Roadmap Phase 1 – MVP Chat → SQL → Oracle Read-only operations Ontology + schema mapping SQL preview Basic UI Phase 2 – Full CRUD & Governance Update/insert workflows Role-based controls Full auditing Data quality assistant Phase 3 – Advanced AI Well log QC agent Seismic metadata intelligence Cross-platform (Petrel, OSDU) connectors Predictive query engine"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Querying Well Data (Priority: P1)

A geoscientist wants to retrieve well header information for a specific field. They type a natural language query like "show me all wells in the 'Poseidon' field" into the chat interface. The system interprets the query, generates the appropriate SQL, executes it against the OpenWorks database, and displays the results in a clear, tabular format.

**Why this priority**: This is the most fundamental read-only use case and demonstrates the core value proposition of the system.

**Independent Test**: This can be tested by providing a natural language query for well data and verifying that the correct data is returned from the database.

**Acceptance Scenarios**:

1. **Given** a user is logged in, **When** they enter "show me all wells in the 'Poseidon' field", **Then** the system displays a table of well header data for all wells where the field name is 'Poseidon'.
2. **Given** a user is logged in, **When** they enter an ambiguous query like "show me wells", **Then** the system asks for clarification, such as "Which field or area are you interested in?".

---

### User Story 2 - Updating Well Status (Priority: P2)

A data manager needs to update the status of a well from "drilling" to "completed". They type "update well 'Poseidon-1' status to 'completed'". The system identifies the intent to update, generates the SQL, and presents it to the user for confirmation, explaining the change. After the user approves, the system executes the update.

**Why this priority**: This introduces the critical write functionality with the necessary safety-gate of user approval.

**Independent Test**: This can be tested by issuing an update command, confirming the generated SQL, and then verifying the data is updated in the database.

**Acceptance Scenarios**:

1. **Given** a user with write permissions is logged in, **When** they enter "update well 'Poseidon-1' status to 'completed'", **Then** the system shows the user the `UPDATE` SQL statement and asks for confirmation before executing it.
2. **Given** a user without write permissions is logged in, **When** they attempt to update data, **Then** the system informs them they do not have the required permissions.

---

### Edge Cases

- What happens when a user requests data from a non-existent table or column?
- How does the system handle extremely large query results (e.g., millions of rows)?
- What happens if the Oracle database connection is lost during an operation?
- How does the system handle concurrent write operations to the same data by multiple users?
- What happens if a user tries to perform a write operation on a read-only field?
- How does the system prevent SQL injection attacks?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept natural language queries in English.
- **FR-002**: The system MUST translate natural language queries into SQL statements compatible with the Oracle OpenWorks schema.
- **FR-003**: The system MUST display a preview of any SQL statement that will modify data (UPDATE, INSERT, DELETE) to the user for approval before execution.
- **FR-004**: The system MUST enforce role-based access control (RBAC) for all database operations.
- **FR-005**: The system MUST log all executed SQL queries, including the user, timestamp, and the query itself.
- **FR-006**: The system MUST present query results in a tabular format.
- **FR-007**: The system MUST ask for clarification if a user's query is ambiguous.

### Key Entities *(include if feature involves data)*

- **Well**: Represents a wellbore with attributes like name, location, status, and associated data.
- **Seismic Survey**: Represents a collection of seismic data with metadata.
- **Log**: Represents a well log with curve data.
- **User**: Represents a system user with associated roles and permissions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of natural language queries for common OpenWorks entities (wells, surveys, logs) are correctly translated to SQL.
- **SC-002**: For read-only queries, the system returns results to the user in under 5 seconds for typical queries.
- **SC-003**: No data-modifying operations are executed without explicit user approval.
- **SC-004**: A complete audit trail of all database operations is available.