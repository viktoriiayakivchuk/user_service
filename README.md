# User Service

A microservice designed for identity, user profiles, and access management within the E-Learning platform ecosystem.

## Technical Stack
- **Framework:** Python, FastAPI, Uvicorn
- **Database:** PostgreSQL, SQLAlchemy, Alembic
- **Message Broker:** RabbitMQ (via `pika` for async domain event publishing)
- **Security:** OAuth2 with JWT Bearer tokens, password hashing with `bcrypt`

## Documentation & Architecture
All architectural specifications, models, and C4 diagrams can be found in the [docs/](docs/) directory:

- **Requirements:** [Requirements Specification](docs/requirements.md) – Functional & Non-functional system requirements.
- **Behaviors:** [Component Behaviors](docs/behaviors.md) – Detailed synchronous & asynchronous service operations.
- **Database:** [Database Schema (DBML)](docs/database_model.dbml) – Database tables definition in DBML.
- **C4 Diagrams & Models:**
  - [System Context Diagram](docs/с4%20System%20context%20diagram.png)
  - [Container Diagram](docs/Conteiner%20diagram(C4).png)
  - [Component Diagram](docs/component_diagram(c4)%202.png) ([PUML Source](docs/component_diagram(c4)_2.puml))
  - [Domain Data Model (ERD)](docs/Domain%20data%20model%20(ERD).png)
  - [Capabilities Decomposition](docs/Capabilities%20decomposition.png)

## API Specifications
The service exposes both synchronous REST endpoints and asynchronous message events:
- **REST API:** [openapi.yaml](openapi.yaml) (Identity registration, authentication, profiles, administrative lockout)
- **Event-driven API:** [asyncapi.yaml](asyncapi.yaml) (Dispatches `UserRegistered` event to RabbitMQ)

## Getting Started

### Prerequisites
- Docker & Docker Compose

### Quick Run
Spin up the service along with PostgreSQL and RabbitMQ:
```bash
docker compose up --build
```
The service will be available at `http://localhost:8000`.
