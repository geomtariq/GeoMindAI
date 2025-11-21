# Feature Specification: GeoMind AI Core

**Feature Branch**: `001-geospatial-ai-interface`
**Created**: 2025-11-22
**Status**: Draft
**Input**: User description: "1. Product Overview GeoMind AI is an AI-driven interface that enables geoscientists, data managers, and subsurface engineers to interact with Landmark OpenWorks (Oracle RDBMS) using natural language. The system interprets user queries, converts them into validated SQL, performs secure read/write operations, and returns formatted results. The system is designed as an external intelligence layer that requires no modification to OpenWorks software, only access to its Oracle database schema. 2. Purpose The purpose of GeoMind AI is to: Provide a plain-English query interface to OpenWorks. Reduce the complexity of querying, updating, and managing subsurface data. Ensure complete safety, auditability, and compliance during database operations. Accelerate workflows related to wells, logs, seismic metadata, markers, and interpretation datasets. Serve as an enterprise-scale assistant bridging geoscience expertise with AI automation. 3. Scope 3.1 Included Functional Domains 3.1.1 Natural Language Understanding Interpret plain-English questions and commands. Detect user intent (retrieve, update, insert, edit, metadata). Translate geoscience terminology into OpenWorks schema tables and columns. Resolve ambiguities through follow-up questions. 3.1.2 Schema-Aware SQL Generation Generate contextually correct SQL based on OpenWorks schema. Validate generated SQL against: Table existence Field existence Allowed joins Permission model Reject unsafe or high-risk SQL operations. 3.1.3 Oracle Database Access Execute read operations across all accessible OpenWorks schemas. Perform controlled write/update operations after user approval. Use parameter binding to avoid SQL injection. Log each executed SQL query with timestamp and user ID. 3.1.4 User Interface Chat-based interface for natural interaction. Tabular view for query results. Query preview (SQL + reasoning). Result export (CSV/Excel). Dark mode for geoscientist workflow environments. 3.1.5 Governance &... [truncated]

## Clarifications

### Session 2025-11-22
- Q: What are the specific permissions for the 'geoscientist' and 'data_manager' roles? → A: Both roles have read/write access.
- Q: How should the system present query results when the number of rows is very large? → A: Paginate the results (e.g., show 100 rows per page) and provide an option to export the full dataset to CSV/Excel.
- Q: What defines a "sensitive write action" and what is the multi-step approval process? → A: All write actions are considered sensitive and require a single-step approval from a data manager.
- Q: What is the strategy for securing the Oracle database credentials that GeoMind AI will use to connect to OpenWorks? → A: Environment variables injected at runtime (e.g., via Kubernetes Secrets, cloud secret managers).
- Q: What additional information, beyond the basic logging, should be included in the audit trail to support full traceability and how will the "rollback registry" function? → A: The audit trail must include a snapshot of the "before" and "after" state of affected records for all write operations, along with the specific user intent (natural language query). The "rollback registry" will be a dedicated, immutable log of all write operations, enabling point-in-time recovery to reverse specific changes if needed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Querying Well Data (Priority: P1)

A geoscientist wants to retrieve well header information for a specific field. They type a natural language query like "show me all wells in the 'Poseidon' field" into the chat interface. The system interprets the query, generates the appropriate SQL, executes it against the OpenWorks database, and displays the results in a clear, tabular format.

**Why this priority**: This is the most fundamental read-only use case and demonstrates the core value proposition of the system.

**Independent Test**: This can be tested by providing a natural language query for well data and verifying that the correct data is returned from the database.

**Acceptance Scenarios**:

1. **Given** a user is logged in, **When** they enter "show me all wells in the 'Poseidon' field", **Then** the system displays a table of well header data for all wells where the field name is 'Poseidon'.
2. **Given** a user is logged in, **When** they enter an ambiguous query like "show me wells", **Then** the system asks for clarification, such as "Which field or area are you interested in?".
3. **Given** a query returns a large number of rows, **When** the system presents the results, **Then** the results are paginated (e.g., 100 rows per page) with navigation controls, and an option to export the full dataset to CSV/Excel is available.

---

### User Story 2 - Updating Well Status (Priority: P2)

A data manager or geoscientist needs to update the status of a well from "drilling" to "completed". They type "update well 'Poseidon-1' status to 'completed'". The system identifies the intent to update, generates the SQL, and presents it to the user for confirmation, explaining the change. After the user approves, the system executes the update.

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
- **FR-004**: The system MUST enforce role-based access control (RBAC). The 'geoscientist' and 'data_manager' roles both have read and write permissions.
- **FR-005**: The system MUST log all executed SQL queries, including the user, timestamp, and the query itself.
- **FR-006**: The system MUST present query results in a tabular format.
- **FR-007**: The system MUST ask for clarification if a user's query is ambiguous.
- **FR-008**: The system MUST paginate large query results (e.g., 100 rows per page) and provide an option to export the full dataset to CSV/Excel.

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
- **SC-005**: Large query results are successfully paginated and exportable, preventing UI performance issues.

## Non-Functional Requirements

### Security

- **NFR-SEC-001**: Enforced user authentication (OIDC/SSO).
- **NFR-SEC-002**: Oracle credentials secured via environment variables injected at runtime (e.g., Kubernetes Secrets, cloud secret managers).
- **NFR-SEC-003**: No direct SQL entry allowed from user.
- **NFR-SEC-004**: All SQL validated via AI + rule engine.

### Auditability and Rollback

- **NFR-AUDIT-001**: The audit trail must include a snapshot of the "before" and "after" state of affected records for all write operations, along with the specific user intent (natural language query).
- **NFR-AUDIT-002**: The "rollback registry" will be a dedicated, immutable log of all write operations, enabling point-in-time recovery to reverse specific changes if needed.
