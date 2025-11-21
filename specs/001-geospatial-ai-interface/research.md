# Research: GeoMind AI Core

This document outlines the technology decisions made during the planning phase for the GeoMind AI Core feature.

## Backend Framework

- **Decision**: FastAPI (Python)
- **Rationale**: The AI/NLP components of the stack are Python-based (LangChain). Using FastAPI for the backend simplifies the technology stack, reduces language context switching, and allows for seamless integration between the API and the AI orchestration layers. FastAPI's performance and modern features (like automatic OpenAPI documentation) are well-suited for this project.
- **Alternatives considered**: Node.js (NestJS) was considered, but the benefits of a unified Python stack outweighed the potential advantages of Node.js for this specific, AI-heavy application.

## Vector Storage

- **Decision**: Chroma
- **Rationale**: Chroma is a specialized, open-source vector database designed for building LLM apps. Its focus on this specific use case makes it a strong choice for managing the embeddings required for the Schema/Ontology Engine. It is simple to set up and is designed to work well with tools like LangChain.
- **Alternatives considered**: pgvector was considered. While it's a good option if a PostgreSQL database is already in use for other application data, Chroma's specialization and focus as a dedicated vector store are better aligned with the project's needs.

## Authentication Provider

- **Decision**: Auth0
- **Rationale**: Auth0 provides a robust, developer-friendly platform for implementing authentication, including enterprise features like SSO which are mentioned in the requirements. It accelerates development by handling the complexities of authentication, allowing the team to focus on core application logic.
- **Alternatives considered**: Azure AD is a strong contender for enterprise environments, but Auth0 offers more flexibility and a quicker startup experience for an MVP. Keycloak is a powerful open-source alternative but requires more self-hosting and management overhead.

## Logging and Monitoring

- **Decision**: Loki & Grafana
- **Rationale**: The Loki & Grafana stack is a modern, lightweight, and cost-effective solution for logging and monitoring, especially in a Kubernetes-native environment. Grafana provides excellent visualization capabilities, and Loki is optimized for efficient log aggregation without the need for full-text indexing of log content, which simplifies operations.
- **Alternatives considered**: The ELK (Elasticsearch, Logstash, Kibana) stack is a powerful but more resource-intensive alternative. For the initial phases of this project, the Loki/Grafana stack provides a better balance of features and operational simplicity.
