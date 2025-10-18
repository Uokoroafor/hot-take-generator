# 🔥 Hot Take Generator

A full-stack application that generates spicy opinions on any topic using AI agents powered by OpenAI and Anthropic models.

## Features

- **Multiple AI Agents**: Choose between OpenAI (GPT) and Anthropic (Claude) models
- **Various Styles**: Generate takes in different styles (controversial, sarcastic, optimistic, etc.)
- **Real-time Generation**: Fast API responses with modern React frontend
- **Responsive Design**: Beautiful, mobile-friendly interface

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **UV**: Fast Python package manager
- **OpenAI API**: GPT models for text generation
- **Anthropic API**: Claude models for text generation
- **Pydantic**: Data validation and settings management

### Frontend
- **React**: Modern UI library with TypeScript
- **Vite**: Fast build tool and dev server
- **CSS3**: Custom styling with gradients and animations

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- UV package manager
- API keys for OpenAI and/or Anthropic

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies with UV:
   ```bash
   uv sync
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   ```

4. Add your API keys to `.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

5. Start the development server:
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser to `http://localhost:5173`

## API Endpoints

### POST `/api/generate`
Generate a hot take on a given topic.

**Request Body:**
```json
{
  "topic": "string",
  "style": "controversial|sarcastic|optimistic|pessimistic|absurd|analytical|philosophical|witty|contrarian",
  "length": "short|medium|long"
}
```

**Response:**
```json
{
  "hot_take": "string",
  "topic": "string",
  "style": "string",
  "agent_used": "string"
}
```

### GET `/api/styles`
Get available hot take styles.

### GET `/api/agents`
Get available AI agents.

## Project Structure

```
hot-take-generator/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agent implementations
│   │   ├── api/             # API routes
│   │   ├── core/            # Configuration and settings
│   │   ├── models/          # Pydantic models
│   │   └── services/        # Business logic
│   ├── tests/               # Backend tests
│   └── pyproject.toml       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   └── ...
│   └── package.json         # Node dependencies
└── README.md
```

## Available Styles

- **Controversial**: Bold, provocative opinions that challenge conventional wisdom
- **Sarcastic**: Witty, sharp commentary with humor
- **Optimistic**: Positive, uplifting perspectives
- **Pessimistic**: Cynical, worst-case scenario viewpoints
- **Absurd**: Completely ridiculous and funny takes
- **Analytical**: Deep, nuanced breakdowns
- **Philosophical**: Thought-provoking questions about life and society
- **Witty**: Clever, memorable one-liners
- **Contrarian**: Always taking the opposite stance from popular opinion

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.