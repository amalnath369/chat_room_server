# Real-Time WebSocket Chat Server

A lightweight real-time chat server using FastAPI WebSockets with topic-based chat rooms, message expiration, and automatic cleanup.

## Features

- Real-time messaging using WebSockets
- Topic-based chat rooms
- Automatic username uniqueness (appends #number if duplicate)
- Message expiration (30 seconds TTL)
- Topic listing command (/list)
- Automatic cleanup of empty topics
- Graceful error handling
- Clean architecture design

## Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional)

## Installation

### Using Docker (Recommended)

1. Clone and run with Docker Compose:
```bash
This project includes a full Docker setup.  
Run the server easily inside a container.

## 1️⃣ Clone the repository
```bash
git clone https://github.com/amalnath369/chat_room_server.git

# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

Then open: http://localhost:8000/client
