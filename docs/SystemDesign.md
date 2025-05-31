# System Design Document
## DrFirst Agentic Business Case Generator

### 1. Architecture Overview

The DrFirst Agentic Business Case Generator follows a microservices architecture with AI agents orchestrated through Google Cloud's Agent Development Kit (ADK).

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Browser Ext    │    │   Mobile App    │
│  (React/TS)     │    │                 │    │   (Future)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   API Gateway   │
                    │   (FastAPI)     │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Agent Orches-  │
                    │    trator       │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Product Manager │    │   Architect     │    │  Data Analyst   │
│     Agent       │    │     Agent       │    │     Agent       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Data Layer    │
                    │  (Firestore)    │
                    └─────────────────┘
```

### 2. System Components

#### 2.1 Frontend Application
- **Technology**: React 18 + TypeScript + Vite
- **UI Framework**: Material-UI (MUI)
- **State Management**: React Query + Context API
- **Authentication**: Firebase Auth
- **Features**:
  - Real-time collaboration
  - Rich text editing
  - Export capabilities
  - Progress tracking

#### 2.2 Backend Services

##### 2.2.1 API Gateway (FastAPI)
- **Purpose**: Central entry point for all client requests
- **Responsibilities**:
  - Authentication & authorization
  - Request routing
  - Rate limiting
  - Logging & monitoring
- **Endpoints**:
  - `/api/v1/auth/*` - Authentication
  - `/api/v1/agents/*` - Agent operations
  - `/api/v1/business-cases/*` - Business case CRUD
  - `/api/v1/admin/*` - Administrative functions

##### 2.2.2 Agent Orchestrator
- **Purpose**: Coordinate multiple AI agents for business case generation
- **Architecture**: Event-driven with message queues
- **Responsibilities**:
  - Agent lifecycle management
  - Task distribution
  - Result aggregation
  - Error handling & retry logic

#### 2.3 AI Agents

##### 2.3.1 Orchestrator Agent
- **Role**: Coordination and workflow management
- **Capabilities**:
  - Parse user requirements
  - Create execution plans
  - Distribute tasks to specialized agents
  - Aggregate results

##### 2.3.2 Product Manager Agent
- **Role**: Business analysis and market research
- **Capabilities**:
  - Market opportunity analysis
  - Competitive landscape research
  - ROI calculations
  - Risk assessment

##### 2.3.3 Architect Agent
- **Role**: Technical planning and implementation
- **Capabilities**:
  - System architecture design
  - Technology recommendations
  - Implementation timeline estimation
  - Technical risk identification

##### 2.3.4 Data Analyst Agent (Future)
- **Role**: Data analysis and insights
- **Capabilities**:
  - Historical data analysis
  - Trend identification
  - Performance projections
  - Metrics recommendations

### 3. Data Architecture

#### 3.1 Database Design (Firestore)

```
Collections:
├── users/
│   ├── {uid}/
│   │   ├── profile: UserProfile
│   │   ├── preferences: UserPreferences
│   │   └── statistics: UserStatistics
├── business_cases/
│   ├── {caseId}/
│   │   ├── metadata: BusinessCaseMetadata
│   │   ├── content: BusinessCaseContent
│   │   ├── versions: BusinessCaseVersion[]
│   │   └── collaborators: Collaborator[]
├── jobs/
│   ├── {jobId}/
│   │   ├── status: JobStatus
│   │   ├── progress: JobProgress
│   │   └── results: JobResults
└── templates/
    ├── {templateId}/
    │   ├── name: string
    │   ├── sections: TemplateSection[]
    │   └── metadata: TemplateMetadata
```

#### 3.2 Data Models

```typescript
interface BusinessCase {
  id: string;
  title: string;
  description: string;
  status: 'draft' | 'in_progress' | 'completed' | 'archived';
  priority: 'low' | 'medium' | 'high' | 'critical';
  created_by: string;
  created_at: Date;
  updated_at: Date;
  sections: BusinessCaseSection[];
  collaborators: string[];
  tags: string[];
}

interface BusinessCaseSection {
  id: string;
  title: string;
  content: string;
  order: number;
  agent_generated: boolean;
  last_updated: Date;
  agent_id?: string;
}
```

### 4. Security Architecture

#### 4.1 Authentication & Authorization
- **Identity Provider**: Google Cloud Identity Platform
- **Token Management**: JWT with refresh tokens
- **Role-Based Access Control (RBAC)**:
  - Admin: Full system access
  - User: Create/edit own business cases
  - Viewer: Read-only access

#### 4.2 Data Security
- **Encryption at Rest**: Firestore native encryption
- **Encryption in Transit**: TLS 1.3
- **API Security**: Rate limiting, input validation
- **Audit Logging**: All actions logged for compliance

### 5. Integration Architecture

#### 5.1 External Services
- **VertexAI**: LLM integration for agent capabilities
- **Google Cloud Storage**: File storage for exports
- **Firebase Functions**: Serverless compute for background tasks
- **Cloud Monitoring**: Observability and alerting

#### 5.2 Internal Integrations (Future)
- **DrFirst CRM**: Customer data integration
- **DrFirst Analytics**: Usage metrics
- **JIRA**: Project management integration
- **Slack**: Notifications and updates

### 6. Deployment Architecture

#### 6.1 Environment Strategy
- **Development**: Local development with Docker Compose
- **Staging**: Google Cloud Run with staging data
- **Production**: Google Cloud Run with auto-scaling

#### 6.2 CI/CD Pipeline
```
GitHub → GitHub Actions → Build → Test → Deploy
                            │
                            ├── Frontend: Build → GCS/CDN
                            └── Backend: Container → Cloud Run
```

### 7. Scalability Considerations

#### 7.1 Frontend Scaling
- **CDN**: Global content delivery
- **Lazy Loading**: Component-based code splitting
- **Caching**: Browser caching strategies

#### 7.2 Backend Scaling
- **Horizontal Scaling**: Cloud Run auto-scaling
- **Database Scaling**: Firestore automatic scaling
- **Agent Scaling**: Queue-based load distribution

### 8. Monitoring & Observability

#### 8.1 Metrics
- **Application Metrics**: Response times, error rates
- **Business Metrics**: Business cases generated, user adoption
- **Infrastructure Metrics**: CPU, memory, storage

#### 8.2 Logging
- **Structured Logging**: JSON format with correlation IDs
- **Log Aggregation**: Google Cloud Logging
- **Log Retention**: 90 days for compliance

#### 8.3 Alerting
- **Error Rate Alerts**: >5% error rate
- **Latency Alerts**: >2s response time
- **Availability Alerts**: <99.9% uptime

### 9. Disaster Recovery

#### 9.1 Backup Strategy
- **Database**: Automated Firestore backups (daily)
- **Storage**: Cross-region replication
- **Code**: Git repository with multiple remotes

#### 9.2 Recovery Procedures
- **RTO**: 4 hours (Recovery Time Objective)
- **RPO**: 24 hours (Recovery Point Objective)
- **Failover**: Automated with health checks

### 10. Performance Requirements

- **API Response Time**: <500ms (95th percentile)
- **Page Load Time**: <2s (first contentful paint)
- **Concurrent Users**: 100+ supported
- **Agent Processing**: <30s for standard business case

### 11. Future Architecture Considerations

- **Multi-Region Deployment**: Global availability
- **Event-Driven Architecture**: Real-time updates
- **Machine Learning Pipeline**: Continuous model improvement
- **Mobile API**: Native mobile app support 