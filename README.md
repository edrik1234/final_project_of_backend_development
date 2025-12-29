# Trivia Telegram Bot – Event-Driven Backend System

This project is an event-driven Trivia Telegram Bot built with a modular backend architecture, fully containerized and orchestrated using Docker Compose.





## High-Level Overview:

The system is composed of multiple Docker containers, each with a single, well-defined responsibility.
All services are orchestrated and monitored using Docker Compose.





## Core goals of the project:

Event-driven backend design.

Asynchronous processing using Kafka.

Stateless authentication with JWT(Bearer Tokens).

Clear separation of concerns between services.

Reproducible and deterministic local development environment.





## Containers
### 1. telebot:

Handles incoming Telegram updates.

Manages game sessions state.

Sends user commands and events to the backend API.

Receives processed responses and delivers messages back to Telegram.

Stateless and fully asynchronous.

**Note**: At the end of a game session, session data is forwarded to external systems (Git-based versioning(through https and GIT_TOKEN), and AWS Lambda pipeline(through event-driven communication with aws credentials)).

### 2. api:

Implemented using FastAPI.

Acts as the system’s entry point.

Responsibilities:

Request validation.

JWT - based authentication.

Producing events to Kafka.

Does not perform heavy business logic.

### 3. logic_worker:

Kafka consumer service.

Processes trivia logic asynchronously.

Responsibilities:

  1)Evaluates user answers.
  
  2)Integrates with the AI service(deepseek) for response generation.
  
  3)Persists results to the database.
  
  4)Writes results to the database.
  
  5)Publishes results back to the system flow.

### 4. postgres:

Relational database service.

Stores:

Users.

Game sessions.

Trivia questions, answers (in Telegram_users).

RequestStatuses.

Runs as a dedicated container with health checks enabled.

### 5. kafka:

Message broker.

Decouples API requests from background processing.

Enables scalable, event-driven communication between services.

Prevents blocking the API during heavy logic execution.

### 6. db_initializer (One-Shot Container):

Dedicated database bootstrap container.

Executes once on system startup.

Waits for PostgreSQL to become healthy.

Creates database schema and initial structures.

Exits automatically after completion.

This approach prevents race conditions and ensures deterministic and reproducible database initialization.





## Key Technologies:

Deepseek

Python 3.11.

Telegram Bot API.

FastAPI.

SQLAlchemy.

Pydantic.

Apache Kafka.

PostgreSQL.

Docker & Docker Compose.

JWT Authentication.

Event-Driven Architecture.

AWS Lambda.

Amazon S3.





## Running the Project:
**docker-compose build --no-cache**
then:
**docker-compose up**


*The system will:*
Build the containers without cache.

Start PostgreSQL.

Initialize the database schema.

Launch all backend services.

Begin processing Telegram events.

Design Highlights.

Stateless services.

Clear separation between API, logic, and messaging layers.

Asynchronous background processing.

Deterministic database initialization.

Fully containerized development environment.




***Notes:***

The project is designed for local development and architectural demonstration purposes.

Credentials and configuration are managed via environment variables.

Demo materials and source videos are provided separately.
