---

description: "Task list for implementing the GeoMind AI Core feature."
---

# Tasks: GeoMind AI Core

**Input**: Design documents from `/specs/001-geospatial-ai-interface/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize project structure and basic tooling for both frontend and backend.

- [X] T001 Create project repository structure (`frontend/src/`, `backend/src/`, `tests/`)
- [X] T002 Initialize Python backend with FastAPI and install dependencies (`backend/pyproject.toml`)
- [X] T003 [P] Initialize React frontend with Next.js and Tailwind CSS (`frontend/package.json`)
- [X] T004 [P] Configure linting (ESLint/Flake8) and code formatting (Prettier/Black) in both projects.
- [X] T005 [P] Setup Docker development environment and Compose files (`docker-compose.yml`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure required before any user story implementation.

- [X] T006 Implement secure configuration management for secrets (e.g., database credentials, API keys) (`backend/src/config.py`)
- [X] T007 [P] Implement authentication and authorization framework using Auth0 (`backend/src/auth/`)
- [X] T008 [P] Setup API routing, middleware for logging and error handling (`backend/src/main.py`)
- [X] T009 Create base Pydantic models for API requests and responses (`backend/src/models/base.py`)
- [X] T010 Configure centralized logging with Loki/Grafana (`backend/src/utils/logger.py`)

**Checkpoint**: Foundation ready – user stories can now be implemented independently.

---

## Phase 3: User Story 1 - Querying Well Data (Priority: P1) 🎯 MVP

**Goal**: A geoscientist can retrieve well header information for a specific field using a natural language query.

**Independent Test**: The user can type "show me all wells in the 'Poseidon' field" and receive a tabular view of the correct well data. The generated SQL is safe and read-only.

### Implementation for User Story 1

- [X] T011 [P] [US1] Create Pydantic models for OpenWorks entities: Well, Seismic Survey, Log (`backend/src/models/openworks.py`)
- [X] T012 [US1] Implement the Schema/Ontology Engine to load and manage OpenWorks schema information (`backend/src/services/schema_engine.py`)
- [X] T013 [US1] Implement the core AI Orchestrator service to interpret user queries using LangChain (`backend/src/services/ai_orchestrator.py`)
- [X] T014 [US1] Implement the SQL Safety Validator for read-only queries (`backend/src/services/sql_validator.py`)
- [X] T015 [US1] Implement the Oracle Data Gateway for executing queries (`backend/src/services/oracle_gateway.py`)
- [X] T016 [US1] Implement the `/chat` API endpoint (`backend/src/api/chat.py`)
- [X] T017 [P] [US1] Create the main chat window component in the frontend (`frontend/src/components/ChatWindow.jsx`)
- [X] T018 [P] [US1] Create the component for displaying tabular results (`frontend/src/components/ResultsTable.jsx`)
- [X] T019 [P] [US1] Create the component for displaying the SQL preview and reasoning (`frontend/src/components/SqlPreview.jsx`)
- [X] T020 [US1] Integrate frontend components and API service calls (`frontend/src/pages/index.js`)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Updating Well Status (Priority: P2)

**Goal**: A data manager can update the status of a well from "drilling" to "completed" with explicit approval.

**Independent Test**: A user with write permissions can type "update well 'Poseidon-1' status to 'completed'", see the generated SQL, approve it, and the database record is updated.

### Implementation for User Story 2

- [ ] T021 [US2] Extend the SQL Safety Validator to handle UPDATE statements (`backend/src/services/sql_validator.py`)
- [ ] T022 [US2] Enhance the AI Orchestrator to detect "update" intent and extract parameters (`backend/src/services/ai_orchestrator.py`)
- [ ] T023 [US2] Implement logic in the `/chat` endpoint to handle the `sql_approval` response type (`backend/src/api/chat.py`)
- [ ] T024 [P] [US2] Create a confirmation modal in the frontend for approving SQL statements (`frontend/src/components/ConfirmationModal.jsx`)
- [ ] T025 [US2] Implement the frontend logic to display the confirmation modal and send approval to the backend (`frontend/src/pages/index.js`)
- [ ] T026 [US2] Add detailed audit logging for all write operations (`backend/src/utils/audit.py`)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: General improvements affecting all user stories.

- [ ] T027 [P] Write comprehensive API documentation using OpenAPI (`docs/api.md`)
- [ ] T028 Perform code cleanup and refactoring across the codebase.
- [ ] T029 [P] Add unit tests for critical business logic in the backend (`backend/tests/unit/`)
- [ ] T030 [P] Add integration tests for the main user flows (`backend/tests/integration/`)
- [ ] T031 Validate and update the `quickstart.md` documentation.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3 & 4)**: All depend on Foundational phase completion.
- **Polish (Phase 5)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2).
- **User Story 2 (P2)**: Can start after User Story 1, as it extends the same core components.

### Parallel Opportunities

- **Setup**: T003, T004, and T005 can run in parallel.
- **Foundational**: T007 and T008 can run in parallel.
- **User Story 1**: T011, T017, T018, and T019 can be started in parallel after the foundational phase is complete.
- **User Story 2**: T024 can be developed in parallel with the backend tasks.
- **Polish**: All tasks in the Polish phase can be worked on in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1.  Complete Phase 1: Setup
2.  Complete Phase 2: Foundational
3.  Complete Phase 3: User Story 1
4.  **STOP and VALIDATE**: Test User Story 1 independently. This provides the core read-only query functionality.
5.  Deploy/demo if ready.
