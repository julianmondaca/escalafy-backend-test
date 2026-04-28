# Analytics Pipeline

## Architecture Overview
This is a robust analytics pipeline designed to ingest, process, and report on events efficiently. The architecture is split into several microservices to handle scale and separate concerns. An ingestion API receives events and queues them, while background workers process these events, handle deduplication, and persist them to a PostgreSQL database.

A reporting API is provided to query the processed data and aggregates, allowing for easy integration with dashboards or external tools. Redis is used as a fast, reliable message queue between the ingestion and processing layers, ensuring high throughput.

## Running Locally
1. Clone the repository.
2. Copy `.env.example` to `.env` and adjust the values if necessary.
3. Run `docker-compose up --build -d` to start all services (PostgreSQL, Redis, API, Worker, Reporting).
4. Run database migrations (instructions to be added later as tools are configured).
5. The API will be available at `http://localhost:8000` and Reporting at `http://localhost:8001`.

## Component Interaction
- **API**: Receives events from clients, validates them, and pushes them to a Redis queue.
- **Worker**: Polls the Redis queue, deduplicates events, and writes batches to the PostgreSQL database.
- **Reporting**: Connects exclusively to PostgreSQL to serve queries for dashboards or analysis.
- **PostgreSQL**: Persists structured event data, sessions, and pre-calculated daily aggregates.
- **Redis**: Acts as an intermediary queue buffering the ingestion load and providing transient storage for deduplication state.

## Why Redis for the Queue?
Redis is selected for its in-memory performance, allowing for extremely fast push and pop operations, which is crucial for handling bursts of incoming events in the ingestion API without dropping them. Its data structures, like Lists or Streams, provide a robust foundation for building a simple, high-throughput queue.

## Guaranteeing At-Least-Once Delivery
At-least-once delivery is ensured by making the workers robust against failures. When a worker pulls an item from Redis, it should not remove it completely until the batch it belongs to is successfully committed to PostgreSQL (e.g., using Redis Streams and consumer groups with explicit ACKs). If a worker crashes before ACKing, another worker will eventually re-process the message.

## Improvements with More Time
With more time, I would replace the custom Redis queue implementation with a more established message broker designed specifically for distributed streaming and stronger durability guarantees, such as Apache Kafka or AWS Kinesis, to better handle extreme scale and long-term event retention.
