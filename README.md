# AI Chat Application

A Streamlit-based chat application with OpenAI integration, conversation management, and persona-based system prompts.

## Setup Environment

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- MongoDB (via Docker or local)
- OpenAI API key

### Installation
```bash
# Clone and setup
git clone <repository-url>
cd hugging
pip install -r requirements.txt

# Environment variables
cp .env.example .env  # Create and configure
export OPENAI_API_KEY="your-api-key"
export MONGO_URI="mongodb://localhost:27017"
```

## Running the Application

### A. Start Streamlit
```bash
streamlit run app.py
```
Access at: http://localhost:8501

### B. Start Infrastructure (Docker)

#### Option 1: Services Only (for local development)
```bash
# Start MongoDB and Qdrant only
docker compose -f docker/local.yml up -d

# Check services are running
docker compose -f docker/local.yml ps
```

#### Option 2: Full Application Stack
```bash
cd docker

# Or use the docker folder version
docker compose up -d

# Check all services are running
docker compose ps

# View logs
docker compose logs -f app
```

#### Option 3: Build and Run App Container Manually
```bash
# Build the Docker image
docker/build.sh

# Run with external services
docker compose -f docker/local.yml up -d  # Start services first
docker run -p 8501:8501 --env-file .env --network hugging_default hugging-chat:latest

# Or run standalone (requires external MongoDB/Qdrant)
docker run -p 8501:8501 --env-file .env hugging-chat:latest
```

### C. Run Tests
```bash
# All tests
./test.sh tests

# Specific test suites
./test.sh tests/unit/app
./test.sh tests/unit/conversations/

# With coverage
./test.sh --cov=conversations --cov=components
```

### D. Code Quality Tools
```bash
# Format and lint code
./format.sh

# Setup pre-commit hooks (one-time)
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files

# Manual tools
ruff check . --fix         # Lint and auto-fix
ruff format .              # Format code
```

## Module Structure

### Core Modules
- **`app.py`** - Main Streamlit application entry point
- **`components/`** - UI components (sidebar, chat input, message display)
- **`conversations/`** - Conversation management, personas, and chat logic
- **`core/`** - Dependency injection container and bootstrap
- **`integrations/`** - External service integrations (OpenAI)
- **`persistence/`** - Data storage (MongoDB, vector store)
- **`pipelines/`** - Data processing pipelines (PDF ingestion)

### Key Features
- **Persona System**: Predefined AI personalities with automatic system prompts
- **Auto-save**: Conversations automatically saved to MongoDB
- **Token Tracking**: Token usage monitoring and display
- **Recent Conversations**: Load and continue previous conversations
- **Multi-step Reasoning**: Optional reasoning workflow for complex queries

### Configuration
Environment variables in `.env`:
```bash
OPENAI_API_KEY=your-key
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=hugging_chat
DEFAULT_CHAT_MODEL=gpt-4o
```

### Architecture
- **DI Container**: Centralized service management
- **Repository Pattern**: Data access abstraction
- **Component-based UI**: Modular Streamlit components
- **Type Safety**: Pydantic models for validation
