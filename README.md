# DrFirst Agentic Business Case Generator

## Build Status

[![Backend CI & Staging CD](https://github.com/drfirst/drfirst-business-case-generator/actions/workflows/backend-ci.yml/badge.svg?branch=develop)](https://github.com/drfirst/drfirst-business-case-generator/actions/workflows/backend-ci.yml)
[![Frontend CI & Firebase CD](https://github.com/drfirst/drfirst-business-case-generator/actions/workflows/frontend-ci-cd.yml/badge.svg?branch=develop)](https://github.com/drfirst/drfirst-business-case-generator/actions/workflows/frontend-ci-cd.yml)
[![Deploy Firestore Rules & Indexes](https://github.com/drfirst/drfirst-business-case-generator/actions/workflows/firestore-deploy.yml/badge.svg?branch=develop)](https://github.com/drfirst/drfirst-business-case-generator/actions/workflows/firestore-deploy.yml)

A comprehensive web application for DrFirst that leverages AI agents to automatically generate comprehensive business cases with full workflow management.

## Project Structure

```
drfirst-business-case-generator/
├── backend/           # Python Backend with FastAPI & AI Agents
├── frontend/          # React/Vite Web Application  
├── shared/            # Shared TypeScript types
├── docs/              # Project documentation (organized by category)
│   ├── architecture/  # System design, PRDs, ADRs
│   ├── deployment/    # CI/CD, infrastructure setup
│   ├── development/   # Setup guides, technical docs
│   ├── testing/       # Testing strategies, guides
│   └── implementation/ # Feature completion summaries
├── tests/             # Cross-component tests
│   ├── e2e/          # End-to-end workflow tests
│   ├── integration/  # Integration tests
│   └── manual/       # Manual testing procedures
├── scripts/           # Project automation scripts
├── config/            # Configuration files
│   ├── docker/       # Docker configurations
│   ├── firebase/     # Firebase settings
│   └── environments/ # Environment-specific configs
└── tools/             # Development utilities
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

### 📋 Quick Links
- [Environment Setup](docs/development/ENVIRONMENT_SETUP.md)
- [E2E Testing](tests/e2e/README.md)
- [CORS Verification](docs/development/CORS_VERIFICATION_GUIDE.md)

### 📚 Main Documentation
- [Architecture & Design](docs/architecture/) - System design, PRDs, ADRs
- [Development Guides](docs/development/) - Setup, technical implementation
- [Deployment](docs/deployment/) - CI/CD, infrastructure, branching
- [Testing](docs/testing/) - Testing strategies and guides
- [Implementation Summaries](docs/implementation/) - Feature completion reports

See [docs/README.md](docs/README.md) for complete documentation index.

## Contributing

Please read our contributing guidelines and follow the established patterns.

## License

Internal DrFirst tool - All rights reserved.
