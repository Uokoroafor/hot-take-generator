# Hot Take Generator

[![CI Pipeline](https://github.com/Uokoroafor/hot-take-generator/actions/workflows/main.yaml/badge.svg)](https://github.com/Uokoroafor/hot-take-generator/actions)
[![Coverage](./backend/coverage.svg)](https://github.com/Uokoroafor/hot-take-generator/tree/main/backend)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A full-stack application that generates spicy opinions on any topic using AI agents powered by OpenAI and Anthropic models.

## Public Project Notes

- This is a fun personal project and not intended for high-stakes use.
- Model outputs can be inaccurate or biased.
- Never commit secrets; use `.env.example` files for configuration templates.

## About
This project was inspired by one of my favourite podcasts, [The Arsenal Opinion Podcast](https://www.le-grove.co.uk/s/the-arsenal-opinion-podcast), which kicks off each episode with a "Hottest of Takes" segment. Where each presenter has to give a bold and, preferably, controversial opinion about anything or anyone related to Arsenal FC. I wanted to capture that same spirit with AI: a tool that can instantly craft witty, controversial, or thought-provoking takes on any topic. Whether it's something serious, silly, or somewhere in between.

## Features

- **Multiple AI Agents**: Choose between OpenAI (GPT) and Anthropic (Claude) models
- **Various Styles**: Generate takes in different styles (controversial, sarcastic, optimistic, etc.)
- **Web Search Integration**: Optionally incorporate recent news and current events into hot takes
- **Real-time Generation**: Fast API responses with modern React frontend
- **Responsive Design**: Beautiful, mobile-friendly interface
- **Comprehensive Testing**: Full test suite with pytest for reliable operation

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework with CORS support
- **UV**: Fast Python package manager and virtual environment management
- **OpenAI API**: GPT models for text generation
- **Anthropic API**: Claude models for text generation
- **Pydantic**: Data validation and settings management (v2 compatible)
- **HTTPX**: Async HTTP client for web search capabilities
- **BeautifulSoup4**: HTML parsing for article content extraction
- **Feedparser**: RSS feed parsing for news integration
- **Pytest**: Comprehensive testing framework with async support

### Frontend
- **React**: Modern UI library with TypeScript
- **Vite**: Fast build tool and dev server
- **CSS3**: Custom styling with gradients and animations

## Quick Start

### Prerequisites
- **For Native Development**: Python 3.11+, Node.js 22+, UV package manager
- **For Docker Development**: Docker and Docker Compose
- API keys for OpenAI and/or Anthropic

### Option 1: Quick Start with Makefile (Recommended)

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/Uokoroafor/hot-take-generator.git
cd hot-take-generator

# Install dependencies and start both servers
make quick-start
```

This will:
- Install backend and frontend dependencies
- Set up environment files
- Start both backend (port 8000) and frontend (port 5173) servers

**Other useful Makefile commands:**
```bash
make help                # Show all available commands
make dev                 # Start both servers
make test               # Run all tests
make docker-up          # Start with Docker
make stop               # Stop all servers
```

### Option 2: Docker Quick Start

If you prefer using Docker:

```bash
# Clone the repository
git clone https://github.com/Uokoroafor/hot-take-generator.git
cd hot-take-generator

# Set up environment file (add your API keys)
make setup-env
# Edit backend/.env to add your API keys

# Start with Docker Compose
docker-compose up
```

**Add your API keys to `backend/.env`:**
```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ENVIRONMENT=development
DEBUG=true
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Docker Environment Configuration

The Docker setup uses multi-stage builds for optimised production images and properly supports environment variables for both development and production:

#### Development Mode

In development mode, environment variables are passed directly to the container:

```bash
# The frontend will use the environment variable from docker-compose.yml
docker-compose up
```

The frontend container receives `VITE_API_BASE_URL=http://localhost:8000` from the compose file.

#### Production Deployments

Production deployment is handled separately:

- Frontend on Vercel
- Backend on Render

Set `VITE_API_BASE_URL` in Vercel to your deployed backend URL.

#### Custom Frontend API URL

To configure a different API endpoint for the frontend:

**Development:**
Edit `docker-compose.yml` line 47:
```yaml
environment:
  - VITE_API_BASE_URL=http://your-custom-api:8000
```

**Production:**
Set `VITE_API_BASE_URL` in your deployment platform (for example, Vercel).

**Important Notes:**
- Frontend environment variables must be prefixed with `VITE_` to be accessible
- Changes to `.env` files require rebuilding the Docker images
- The `.env` file is excluded from Docker images for security (use build args instead)
- Environment variables are embedded at BUILD time for production (not runtime)

### Option 3: Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment and install dependencies with UV:
   ```bash
   uv venv
   uv sync
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   ```

5. Add your API keys to `.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ENVIRONMENT=development
   DEBUG=true
   ```

6. Start the development server:
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

   The default `.env` file contains:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

   Adjust if your backend is running on a different URL.

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open your browser to `http://localhost:5173`

## API Endpoints

### POST `/api/generate`
Generate a hot take on a given topic.

**Request Body:**
```json
{
  "topic": "string (required, cannot be empty)",
  "style": "controversial|sarcastic|optimistic|pessimistic|absurd|analytical|philosophical|witty|contrarian",
  "length": "short|medium|long",
  "use_web_search": "boolean (default: false)",
  "max_articles": "integer (default: 3, max articles to fetch for web search)"
}
```

**Response:**
```json
{
  "hot_take": "string",
  "topic": "string",
  "style": "string",
  "agent_used": "string",
  "web_search_used": "boolean",
  "news_context": "string|null (recent news used in generation)"
}
```

### GET `/api/styles`
Get available hot take styles.

### GET `/api/agents`
Get available AI agents.

## Testing

The backend includes a comprehensive test suite covering all functionality:

### Running Tests

```bash
cd backend

# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py

# Run tests excluding external API calls
pytest -m "not external"
```

### Test Categories

- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test service interactions and API endpoints
- **External Tests**: Test real API integrations (marked with `@pytest.mark.external`)

### Test Markers

- `unit`: Unit tests for isolated functionality
- `integration`: Integration tests for component interaction
- `slow`: Tests that may take longer to run
- `external`: Tests requiring external API access (internet connection)

## Project Structure

```
hot-take-generator/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agent implementations (OpenAI, Anthropic)
│   │   ├── api/             # FastAPI routes and endpoints
│   │   ├── core/            # Configuration and settings management
│   │   ├── models/          # Pydantic models and schemas
│   │   └── services/        # Business logic and external integrations
│   │       ├── hot_take_service.py     # Main hot take generation logic
│   │       └── web_search_service.py   # News and web search integration
│   ├── tests/               # Comprehensive test suite
│   │   ├── test_api.py      # API endpoint tests
│   │   ├── test_agents.py   # AI agent tests
│   │   ├── test_config.py   # Configuration tests
│   │   ├── test_models.py   # Model validation tests
│   │   ├── test_services.py # Service logic tests
│   │   └── test_web_search.py # Web search functionality tests
│   ├── pytest.ini           # Pytest configuration
│   ├── pyproject.toml       # Python dependencies and project config
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   └── ...
│   └── package.json         # Node dependencies
├── docker-compose.yml       # Docker development setup
└── README.md
```

## Available Styles

- **Controversial**: Bold, provocative opinions that challenge conventional wisdom
- **Sarcastic**: Witty, sharp commentary with humour
- **Optimistic**: Positive, uplifting perspectives
- **Pessimistic**: Cynical, worst-case scenario viewpoints
- **Absurd**: Completely ridiculous and funny takes
- **Analytical**: Deep, nuanced breakdowns
- **Philosophical**: Thought-provoking questions about life and society
- **Witty**: Clever, memorable one-liners
- **Contrarian**: Always taking the opposite stance from popular opinion

## Development Commands (Makefile)

The project includes a comprehensive Makefile for easy development. Here are the most useful commands:

### Quick Start Commands
```bash
make quick-start         # Install dependencies and start development servers
make quick-start-docker  # Setup and start with Docker
```

### Development
```bash
make dev                 # Start both backend and frontend servers
make dev-backend        # Start only backend server
make dev-frontend       # Start only frontend server
make stop               # Stop all development servers
make restart            # Restart all servers
```

### Testing
```bash
make test               # Run all tests
make test-backend       # Run only backend tests
make test-coverage      # Run tests with coverage report
make test-watch         # Run tests in watch mode
```

### Code Quality
```bash
make lint               # Run linting on all code
make format             # Format all code
make check              # Run all quality checks (lint + test)
```

### Docker
```bash
make docker-up          # Start with Docker Compose
make docker-up-detached # Start Docker in background
make docker-down        # Stop Docker services
make docker-logs        # View Docker logs
make docker-clean       # Clean up Docker resources
```

### Utilities
```bash
make help               # Show all available commands
make info               # Show development information
make health             # Check if services are running
make clean              # Clean up build artefacts
```

### Documentation
```bash
cd backend
uv run mkdocs serve     # Serve docs locally at http://localhost:8000
uv run mkdocs build     # Build static site to backend/site/
```

## Troubleshooting

### Common Issues

**Virtual Environment Conflicts**
```bash
# If you see VIRTUAL_ENV warnings, remove and recreate the virtual environment
rm -rf .venv
uv venv
uv sync
```

**Pytest Unknown Markers**
```bash
# Ensure pytest.ini is properly configured with custom markers
pytest --markers  # Should show 'external', 'unit', 'integration', 'slow'
```

**Empty Topic Validation Errors**
- The API now validates that topics are not empty or whitespace-only
- Ensure your requests include a meaningful topic string

**Timezone Issues in Tests**
- All datetime objects in tests should use `datetime.now(timezone.utc)`
- The web search service uses timezone-aware UTC datetimes


## 🧭 Roadmap / TODO

High-level improvements planned for upcoming releases:
- Add production deployment setup (Docker, Fly.io, Vercel)
- Expand test coverage with frontend + integration tests
- Introduce caching and streaming responses
- Add CI/CD workflows

For a detailed roadmap and task breakdown, see [TODO.md](./TODO.md).


### Development Tips

- Use `pytest -v` for verbose test output
- Run `pytest -m "not external"` to skip tests requiring internet connection
- Check `http://localhost:8000/docs` for interactive API documentation
- Environment variables are automatically loaded from `.env` file

## Contributing

- See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution workflow.
- Community behaviour expectations are in [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).

## License

MIT License - see LICENSE file for details.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
