# DrFirst Agentic Business Case Generator

A comprehensive web application for DrFirst that leverages AI agents to automatically generate comprehensive business cases with full workflow management.

## Project Structure

```
drfirst-business-case-gen/
├── frontend/          # React/Vite Web Application
├── backend/           # Python Backend with ADK Agents
├── shared/            # Shared TypeScript types
├── scripts/           # Helper scripts
├── archive/           # Archived/deprecated components
└── docs/              # Project documentation
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker (optional)

### Development Setup

1. Clone the repository
2. Set up the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.template .env
   # Configure your environment variables
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   cp .env.template .env
   # Configure your environment variables
   ```

### Running the Application

- Backend: `cd backend && python -m app.main`
- Frontend: `cd frontend && npm run dev`
- Visit: http://localhost:4000

## Documentation

- [Product Requirements Document](docs/PRD.md)
- [System Design](docs/SystemDesign.md)
- [Architecture Decision Records](docs/ADR/)

## Contributing

Please read our contributing guidelines and follow the established patterns.

## License

Internal DrFirst tool - All rights reserved. 