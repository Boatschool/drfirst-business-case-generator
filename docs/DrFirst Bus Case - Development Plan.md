**DrFirst Agentic Business Case Generator \- Development Plan**  
**Version:** 1.0  
**Date:** \[Current Date\]  
**Based on:** PRD Version 2.0, System Design Version 1.0  
**Core Principle:** Tasks are designed to be low complexity. Implementation tasks implicitly include unit/integration tests. Design/Define tasks do not include testing.

---

**Phase 1: GCP Foundation & Core Services Setup**

* **Focus:** Establish the GCP project, enable all necessary APIs, set up Firestore, GCS, GCIP, Secret Manager, Logging, Monitoring, Cloud Build, Artifact Registry, and define initial IAM.  
* **Status:** COMPLETE.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 1.1 | **GCP Project & Core Services Setup** |  |  |  |  |  |
| 1.1.1 | Create and Configure new GCP Project for "DrFirst Agentic Business Case Generator" | COMPLETE | highest | low | (GCP Account Access) | Refer to SDD Section 8\. |
| 1.1.2 | Enable Required GCP APIs (Vertex AI, Cloud Run, Firestore, GCS, GCIP, Secret Manager, Logging, Monitoring, Pub/Sub, Cloud Build, Artifact Registry, API Gateway) | COMPLETE | highest | low | 1.1.1 | List from SDD Section 8\. |
| 1.1.3 | Set up Cloud Firestore Database (Native mode, initial region selection, basic security rules stub) | COMPLETE | highest | low | 1.1.2 | SDD Section 4.4 & 7\. Define initial empty collections from SDD (businessCases, users, rateCards, pricingTemplates, auditLogs). |
| 1.1.4 | Set up Google Cloud Storage (GCS) Buckets (e.g., for PRD attachments, agent artifacts \- if any) with initial security policies | COMPLETE | high | low | 1.1.2 | SDD Section 8\. Consider separate buckets for different data types if needed. |
| 1.1.5 | Set up Google Cloud Identity Platform (GCIP) \- Enable, basic configuration (e.g., select providers \- email/password for now) | COMPLETE | highest | low | 1.1.2 | SDD Section 4.2 (Auth Service) & 8\. Future DrFirst SSO integration will build on this. |
| 1.1.6 | Set up Secret Manager: Store initial placeholder secrets (e.g., API keys, DB credentials if not service account based) | COMPLETE | high | low | 1.1.2 | SDD Section 9\. |
| 1.1.7 | Define initial IAM Roles and Permissions for development team and core service accounts (e.g., Cloud Run invoker, Firestore user) | COMPLETE | highest | low | 1.1.1, 1.1.2 | SDD Section 9\. Focus on least privilege. |
| 1.1.8 | Set up Basic Logging & Monitoring: Ensure default logs are captured, create a basic dashboard stub in Cloud Monitoring | COMPLETE | medium | low | 1.1.1, 1.1.2 | SDD Section 8\. |
| 1.1.9 | Set up Cloud Build & Artifact Registry: Basic triggers for future CI/CD (placeholder build file) | COMPLETE | medium | low | 1.1.1, 1.1.2 | SDD Section 8\. |

---

**Phase 2: Backend Scaffolding & ADK Orchestrator Stub**

* **Focus:** Set up the ADK development environment, create the initial Orchestrator Agent structure using ADK, implement a basic "Echo" tool, and set up the Cloud Run service stub for the Application Server. Define core Firestore data models more concretely.  
* **Status:** Partially complete.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 2.1 | **ADK & Orchestrator Setup** |  |  |  |  |  |
| 2.1.1 | Set up ADK Development Environment locally (Python, ADK libraries) | COMPLETE | highest | low | (Python installed) | SDD Section 4.2. Refer to Google ADK documentation. |
| 2.1.2 | Create initial "Orchestrator Agent" project structure using ADK | COMPLETE | highest | low | 2.1.1 | SDD Section 5\. This will be the main agent managing workflow. |
| 2.1.3 | Implement a basic "EchoTool" for the Orchestrator Agent (takes input string, returns it) \- local test | COMPLETE | high | low | 2.1.2 | Simple ADK tool for testing agent invocation. |
| 2.1.4 | Define main function/entry point for Orchestrator Agent to handle requests (e.g., process an "echo" request using EchoTool) | COMPLETE | high | low | 2.1.3 |  |
| 2.2 | **Application Server (Cloud Run) & API Scaffolding** |  |  |  |  |  |
| 2.2.1 | Create Python Flask/FastAPI project for Application Server (to host ADK agents) | COMPLETE | highest | low | (Python installed) | SDD Section 4.2. This will be containerized for Cloud Run. |
| 2.2.2 | Implement a basic health check endpoint (e.g., /health) in the Application Server | COMPLETE | high | low | 2.2.1 | For Cloud Run liveness/readiness probes. |
| 2.2.3 | Implement an API endpoint (e.g., /api/v1/invoke\_agent) in Application Server to receive requests and call the Orchestrator Agent | COMPLETE | high | low | 2.1.4, 2.2.1 | This endpoint will initially call the "echo" functionality of the orchestrator. Request/response format stub. |
| 2.2.4 | Create Dockerfile for the Application Server | COMPLETE | high | low | 2.2.1 | To containerize the Python application. |
| 2.2.5 | Deploy initial Application Server stub to Cloud Run (manual deployment for now) | COMPLETE | high | low | 1.1.2 (Cloud Run API), 2.2.4 | Test health check and basic agent invocation endpoint. |
| 2.2.6 | Set up API Gateway: Create API config and route for the /api/v1/invoke\_agent endpoint on Cloud Run | COMPLETE | high | low | 1.1.2 (API Gateway API), 2.2.5 | SDD Section 4.2. Initially no auth for easy testing. |
| 2.3 | **Firestore Data Model Definition (Code)** |  |  |  |  |  |
| 2.3.1 | Define TypeScript interfaces/Python Pydantic models for businessCases collection (core fields from SDD Section 7\) | COMPLETE | high | low | 1.1.3 | Store these in a shared types library if frontend and backend are in different repos. |
| 2.3.2 | Define TypeScript interfaces/Python Pydantic models for users collection (core fields from SDD Section 7\) | COMPLETE | high | low | 1.1.3 |  |
| 2.3.3 | Define TypeScript interfaces/Python Pydantic models for rateCards, pricingTemplates, auditLogs (core fields) | COMPLETE | medium | low | 1.1.3 |  |

---

**Phase 3: Frontend Foundation & Authentication (GCIP)**

* **Focus:** Set up the React frontend project (Vite), implement GCIP authentication using an abstracted service layer, create basic app layout, and routing.  
* **Status:** Partially complete.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 3.1 | **React Frontend Project Setup** |  |  |  |  |  |
| 3.1.1 | Create new React project using Vite \+ TypeScript template | COMPLETE | highest | low | (Node.js, npm/yarn installed) | SDD Section 4.1. |
| 3.1.2 | Set up basic folder structure (e.g., src/components, src/pages, src/services, src/contexts, src/config, src/hooks) | COMPLETE | highest | low | 3.1.1 | Good practice for organization. |
| 3.1.3 | Install and configure ESLint, Prettier for code quality | COMPLETE | high | low | 3.1.1 |  |
| 3.1.4 | Set up basic routing (e.g., react-router-dom) with placeholder pages: /login, /dashboard, / (home/redirect) | COMPLETE | high | low | 3.1.1 |  |
| 3.1.5 | Create basic App Layout component (e.g., AppLayout.tsx with Header, Sidebar stub, Main Content area) | COMPLETE | high | low | 3.1.1 | This will house the main application interface. |
| 3.2 | **GCIP Authentication Abstraction Layer** Inspired by the example plan's abstraction. |  |  |  |  |  |
| 3.2.1 | Create src/config/gcip.ts for GCIP SDK initialization (using environment variables for config) | COMPLETE | highest | low | 1.1.5, 3.1.1 | Store GCIP project config (apiKey, authDomain, etc.). |
| 3.2.2 | Define src/services/auth/AuthService.ts interface (e.g., signIn, signUp, signOut, onAuthStateChanged, getCurrentUser) | COMPLETE | highest | low | 3.1.2 |  |
| 3.2.3 | Create src/services/auth/GCIPAuthAdapter.ts implementing AuthService using GCIP SDK | COMPLETE | highest | low | 3.2.1, 3.2.2 |  |
| 3.2.4 | Create src/services/auth/index.ts (Auth Service Factory) to provide GCIPAuthAdapter instance | COMPLETE | high | low | 3.2.3 |  |
| 3.3 | **Authentication UI & Context** |  |  |  |  |  |
| 3.3.1 | Create src/contexts/AuthContext.tsx using the abstract authService to manage auth state and provide it to components | COMPLETE | highest | low | 3.2.4 |  |
| 3.3.2 | Implement LoginPage.tsx component with basic email/password form, using authService.signIn() | COMPLETE | highest | low | 3.1.4, 3.3.1 | Basic UI, no styling focus yet. |
| 3.3.3 | Implement SignUpPage.tsx component (if direct sign-up needed, or adapt for admin-invited users later) | COMPLETE | high | low | 3.1.4, 3.3.1 |  |
| 3.3.4 | Implement basic Header.tsx component showing login/logout button and user email (if logged in) using AuthContext | COMPLETE | high | low | 3.1.5, 3.3.1 | Done as part of AppLayout.tsx |
| 3.3.5 | Implement ProtectedRoute component/logic to restrict access to /dashboard based on auth state from AuthContext | COMPLETE | highest | low | 3.1.4, 3.3.1 | Done as part of App.tsx routing setup |
| 3.4 | **Backend GCIP Token Validation** |  |  |  |  |  |
| 3.4.1 | Update Application Server (Python): Add middleware/decorator to validate GCIP ID tokens for protected API endpoints | COMPLETE | highest | low | 1.1.5, 2.2.3 | Use Firebase Admin SDK (Python) for token verification. |
| 3.4.2 | Secure the /api/v1/invoke\_agent endpoint; test that only authenticated requests from frontend pass | COMPLETE | high | low | 2.2.6 (API Gateway), 3.3.2, 3.4.1 | Frontend will need to attach ID token to API requests. Update API Gateway config for auth. |

---

**Phase 4: Agent-UI (AG-UI) Communication & Initial Business Case Flow**

* **Focus:** Implement basic AG-UI client in the frontend, connect it to the Orchestrator Agent via the Application Server, implement the "Intake Agent" logic, and create/display a PRD draft based on user input.  
* **Status:** All tasks todo.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 4.1 | **AG-UI Client Setup (Frontend)** |  |  |  |  |  |
| 4.1.1 | Define src/services/agent/AgentService.ts interface for agent communication (e.g., initiateCase, provideFeedback, onAgentUpdate) | COMPLETE | highest | low | 3.1.2 |  |
| 4.1.2 | Implement basic HttpAgentAdapter.ts for AgentService to call the backend /api/v1/invoke\_agent endpoint | COMPLETE | highest | low | 3.4.2, 4.1.1 | This adapter will handle sending requests to the backend. onAgentUpdate might initially be polled or use a simple WebSocket stub if needed later. |
| 4.1.3 | Create src/contexts/AgentContext.tsx to manage interaction state with the agent system (e.g., current case ID, agent messages, loading state) | COMPLETE | high | low | 3.1.2, 4.1.2 |  |
| 4.2 | **Orchestrator & Intake Agent Logic (Backend \- ADK)** |  |  |  |  |  |
| 4.2.1 | Enhance Orchestrator Agent: Define states for a business case lifecycle (e.g., INTAKE, PRD\_DRAFTING, PRD\_REVIEW) | COMPLETE | highest | low | 2.1.2 | SDD Section 6.3 (MCP State Management). |
| 4.2.2 | Implement IntakeAgent logic within Orchestrator (or as a separate called agent): Prompt user for initial project details (via AG-UI) | COMPLETE | highest | low | 2.1.2, 4.2.1 | For now, this could be a simple "ask for problem statement" prompt. The orchestrator will manage sending this prompt to UI. |
| 4.2.3 | Orchestrator: Store initial user input from IntakeAgent into a new businessCases document in Firestore | COMPLETE | highest | low | 2.3.1, 4.2.2 | Store with status: INTAKE\_COMPLETE. |
| 4.3 | **Product Manager Agent Stub & PRD Drafting (Backend \- ADK)** |  |  |  |  |  |
| 4.3.1 | Create ProductManagerAgent stub (ADK agent structure) | COMPLETE | highest | low | 2.1.2 | SDD Section 5\. |
| 4.3.2 | ProductManagerAgent: Implement logic to take user's problem statement (from Firestore) and generate a very basic PRD draft using Vertex AI | COMPLETE | high | low | 1.1.2 (Vertex AI API), 2.3.1, 4.3.1 | Prompt: "Based on this problem statement: \[input\], write a one-paragraph PRD overview." |
| 4.3.3 | Orchestrator: After intake, invoke ProductManagerAgent and store the generated PRD draft in the businessCases Firestore document | COMPLETE | highest | low | 4.2.3, 4.3.2 | Update status to PRD\_DRAFTED. |
| 4.4 | **Displaying PRD Draft (Frontend)** |  |  |  |  |  |
| 4.4.1 | Create DashboardPage.tsx: List existing business cases for the logged-in user (read from Firestore via a new backend API endpoint) | todo | high | low | 3.3.5, 4.1.3 | New backend endpoint needed: /api/v1/cases (GET). |
| 4.4.2 | Create BusinessCaseDetailPage.tsx: Display basic details of a selected business case, including the PRD draft from Firestore | todo | high | low | 4.4.1 | Fetch full case details: /api/v1/cases/{caseId} (GET). |
| 4.4.3 | Implement "New Business Case" button/flow on DashboardPage.tsx to trigger the IntakeAgent via AgentService | todo | highest | low | 4.1.2, 4.2.2, 4.4.1 | This will initiate the AG-UI conversation for intake. UI needs a text input and send button. |
| 4.4.4 | Basic UI in BusinessCaseDetailPage.tsx to show conversational prompts from Intake Agent & display final PRD draft | todo | high | low | 4.1.3, 4.2.2, 4.3.3, 4.4.2 | For now, agent messages can be simple text displays. PRD draft can be a read-only text area. |

---

**Phase 5: HITL for PRD & Core Agent Enhancements**

* **Focus:** Implement basic HITL for PRD review (editing/approving), enhance ProductManagerAgent with more structured PRD generation, and introduce ArchitectAgent stub.  
* **Status:** All tasks todo.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 5.1 | **PRD Review & Editing (Frontend)** |  |  |  |  |  |
| 5.1.1 | Enhance BusinessCaseDetailPage.tsx: Allow editing of the PRD draft (e.g., using a simple textarea or a basic rich text editor) | todo | high | low | 4.4.4 |  |
| 5.1.2 | Implement "Save PRD Draft" button on BusinessCaseDetailPage.tsx to update the PRD in Firestore (via backend API endpoint) | todo | high | low | 5.1.1 | New backend endpoint: /api/v1/cases/{caseId}/prd (PUT). |
| 5.1.3 | Implement "Submit PRD for Review" button, updating case status in Firestore (via backend API) | todo | high | low | 5.1.2 | Updates status to PRD\_PENDING\_APPROVAL. Backend API: /api/v1/cases/{caseId}/status (PUT). |
| 5.2 | **PRD Approval Logic (Simplified)** |  |  |  |  |  |
| 5.2.1 | Orchestrator/ApprovalAgent Stub: Logic to identify next approver (for V1, can be fixed or self-approval by initiator) | todo | medium | low | 4.3.3 | SDD Section 5 (ApprovalAgent). |
| 5.2.2 | Frontend: If user is designated approver for PRD, show "Approve PRD" / "Reject PRD" buttons on BusinessCaseDetailPage.tsx | todo | medium | low | 5.1.3, 5.2.1 | This requires fetching case details that include who can approve the current stage. |
| 5.2.3 | Implement "Approve PRD" / "Reject PRD" functionality to update case status and log approval action (via backend API) | todo | medium | low | 5.2.2 | Updates status to PRD\_APPROVED or PRD\_REJECTED. Log to auditLogs. |
| 5.3 | **ProductManagerAgent Enhancement (Backend \- ADK)** |  |  |  |  |  |
| 5.3.1 | ProductManagerAgent: Refine PRD generation prompt to create a more structured PRD (e.g., sections for Overview, Goals, User Stories stubs) | todo | high | low | 4.3.2 | Output should ideally be structured (e.g., JSON or Markdown with clear sections). |
| 5.3.2 | ProductManagerAgent: Incorporate context from linked Confluence/Jira (if URLs provided during intake) \- basic "summarize this page" capability | todo | medium | low | 4.3.2 | Requires ability to fetch web page content (simple GET request for now, no complex parsing). Update prompt to use this context. document\_retrieval\_agent concept. |
| 5.4 | **ArchitectAgent Stub (Backend \- ADK)** |  |  |  |  |  |
| 5.4.1 | Create ArchitectAgent stub (ADK agent structure) | todo | high | low | 2.1.2 | SDD Section 5\. |
| 5.4.2 | Orchestrator: If PRD is approved, invoke ArchitectAgent with the approved PRD content | todo | high | low | 5.2.3, 5.4.1 |  |
| 5.4.3 | ArchitectAgent: Implement basic logic to generate a placeholder system design (e.g., "System will use a microservices architecture on GCP.") | todo | high | low | 5.4.2 | Store this in businessCases document. Update status to SYSTEM\_DESIGN\_DRAFTED. |
| 5.5 | **Display System Design (Frontend)** |  |  |  |  |  |
| 5.5.1 | BusinessCaseDetailPage.tsx: Display System Design draft if available | todo | high | low | 4.4.2, 5.4.3 | Similar to displaying PRD draft. |

---

**Phase 6: Cost & Revenue Stubs, Admin UI Basics**

* **Focus:** Introduce stubs for PlannerAgent, CostAnalystAgent, SalesValueAnalystAgent. Implement basic Admin UI for managing rate cards (read-only initially).  
* **Status:** All tasks todo.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 6.1 | **PlannerAgent & CostAnalystAgent Stubs (Backend \- ADK)** |  |  |  |  |  |
| 6.1.1 | Create PlannerAgent stub (ADK agent structure) | todo | high | low | 2.1.2 | SDD Section 5\. |
| 6.1.2 | Orchestrator: After System Design drafted (or approved later), invoke PlannerAgent | todo | high | low | 5.4.3, 6.1.1 |  |
| 6.1.3 | PlannerAgent: Implement placeholder logic (e.g., "Estimated effort: 100 hours Developer, 20 hours PM") | todo | high | low | 6.1.2 | Store in businessCases. Update status. |
| 6.1.4 | Create CostAnalystAgent stub (ADK agent structure) | todo | high | low | 2.1.2 |  |
| 6.1.5 | Orchestrator: Invoke CostAnalystAgent after PlannerAgent | todo | high | low | 6.1.3, 6.1.4 |  |
| 6.1.6 | CostAnalystAgent: Placeholder logic (e.g., "Estimated cost: $10,000" \- reads a default rate from a new rateCards Firestore stub entry) | todo | high | low | 1.1.3 (rateCards), 6.1.5 | Store in businessCases. Update status. |
| 6.2 | **SalesValueAnalystAgent Stub (Backend \- ADK)** |  |  |  |  |  |
| 6.2.1 | Create SalesValueAnalystAgent stub (ADK agent structure) | todo | high | low | 2.1.2 | SDD Section 5\. |
| 6.2.2 | Orchestrator: Invoke SalesValueAnalystAgent (e.g., after PRD approval) | todo | high | low | 5.2.3, 6.2.1 |  |
| 6.2.3 | SalesValueAnalystAgent: Placeholder logic (e.g., "Projected value: Low $5k, Base $15k, High $30k" \- reads from pricingTemplates stub) | todo | high | low | 1.1.3 (pricingTemplates), 6.2.2 | Store in businessCases. Update status. |
| 6.3 | **Display Financial Stubs (Frontend)** |  |  |  |  |  |
| 6.3.1 | BusinessCaseDetailPage.tsx: Display Cost Estimate and Value Projection if available | todo | high | low | 4.4.2, 6.1.6, 6.2.3 | Read-only display. |
| 6.4 | **Admin UI Foundation** |  |  |  |  |  |
| 6.4.1 | Create basic AdminPage.tsx accessible via routing, protected for Admin role (role check to be implemented later) | todo | medium | low | 3.1.4 | For now, access can be unrestricted for testing. |
| 6.4.2 | AdminPage.tsx: Implement UI to display Rate Cards (read-only list from Firestore via new backend API endpoint) | todo | medium | low | 1.1.3 (rateCards), 6.4.1 | New API: /api/v1/admin/rate-cards (GET). |
| 6.4.3 | AdminPage.tsx: Implement UI to display Pricing Templates (read-only list from Firestore via new backend API endpoint) | todo | medium | low | 1.1.3 (pricingTemplates), 6.4.1 | New API: /api/v1/admin/pricing-templates (GET). |

---

**Phase 7: Admin UI Enhancements & Role-Based Access Control (RBAC)**

* **Focus:** Implement CRUD operations for Rate Cards and Pricing Templates in the Admin UI. Implement basic RBAC for accessing Admin features and potentially for approval steps.  
* **Status:** All tasks todo.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 7.1 | **Admin CRUD for Rate Cards** |  |  |  |  |  |
| 7.1.1 | AdminPage.tsx: Add "Create New Rate Card" button and form (name, roles with rates) | todo | medium | low | 6.4.2 |  |
| 7.1.2 | Backend API: Implement /api/v1/admin/rate-cards (POST) to create a new rate card in Firestore | todo | medium | low | 2.3.3 (rateCards model), 7.1.1 | Ensure validation of input. |
| 7.1.3 | AdminPage.tsx: Add "Edit" and "Delete" functionality for existing rate cards | todo | medium | low | 6.4.2 | "Delete" might be a soft delete (mark inactive). |
| 7.1.4 | Backend API: Implement /api/v1/admin/rate-cards/{cardId} (PUT, DELETE) to update/delete rate cards | todo | medium | low | 7.1.3 |  |
| 7.2 | **Admin CRUD for Pricing Templates** |  |  |  |  |  |
| 7.2.1 | AdminPage.tsx: Add "Create New Pricing Template" button and form (name, structure definition \- simple for now) | todo | medium | low | 6.4.3 | Structure definition could be a JSON text area initially. |
| 7.2.2 | Backend API: Implement /api/v1/admin/pricing-templates (POST) to create a new pricing template | todo | medium | low | 2.3.3 (pricingTemplates model), 7.2.1 |  |
| 7.2.3 | AdminPage.tsx: Add "Edit" and "Delete" functionality for existing pricing templates | todo | medium | low | 6.4.3 |  |
| 7.2.4 | Backend API: Implement /api/v1/admin/pricing-templates/{templateId} (PUT, DELETE) to update/delete pricing templates | todo | medium | low | 7.2.3 |  |
| 7.3 | **Role-Based Access Control (RBAC) Implementation** |  |  |  |  |  |
| 7.3.1 | users Firestore Collection: Add systemRole field (e.g., "ADMIN", "BUSINESS\_USER", "DEVELOPER", "SALES\_MANAGER\_APPROVER") | todo | high | low | 2.3.2 | Define initial roles based on PRD User Roles. |
| 7.3.2 | GCIP Custom Claims: On user creation/update (e.g., via an admin function), set a custom claim for systemRole based on Firestore users data | todo | high | low | 1.1.5, 3.4.1, 7.3.1 | This allows roles to be easily accessible from the ID token. Requires a backend Cloud Function for managing custom claims. |
| 7.3.3 | Frontend: Update AuthContext to parse and store systemRole from GCIP ID token's custom claims | todo | high | low | 3.3.1, 7.3.2 |  |
| 7.3.4 | Frontend: Protect AdminPage.tsx route so only users with "ADMIN" role can access it | todo | high | low | 6.4.1, 7.3.3 | Update ProtectedRoute logic. |
| 7.3.5 | Backend API: Secure Admin API endpoints (/api/v1/admin/\*) to only allow users with "ADMIN" role (check custom claim from ID token) | todo | high | low | 3.4.1, 7.1.2, 7.1.4, 7.2.2, 7.2.4, 7.3.2 | Update API Gateway or Application Server middleware. |
| 7.3.6 | Admin UI: Basic user management UI stub (list users, view current role \- no role editing yet) | todo | medium | low | 6.4.1, 7.3.1 | New API: /api/v1/admin/users (GET). |

---

**Phase 8: Full HITL for Technical & Financials, FinancialModelAgent**

* **Focus:** Implement HITL (review, edit, approve) for System Design, Cost Estimates, and Revenue Projections. Implement the FinancialModelAgent to consolidate financials.  
* **Status:** All tasks todo.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 8.1 | **HITL for System Design** |  |  |  |  |  |
| 8.1.1 | Orchestrator: Update status to SYSTEM\_DESIGN\_PENDING\_REVIEW after ArchitectAgent runs. Define who can review (e.g., "DEVELOPER" role). | todo | high | low | 5.4.3, 7.3.1 |  |
| 8.1.2 | BusinessCaseDetailPage.tsx: Allow editing of System Design draft. Add "Submit System Design for Approval" button. | todo | high | low | 5.5.1 | Similar to PRD editing/submission. Backend API: /api/v1/cases/{caseId}/system-design (PUT). |
| 8.1.3 | Frontend: Show "Approve/Reject System Design" buttons for users with appropriate role (e.g., "DEVELOPER" or a designated tech lead). | todo | high | low | 7.3.3, 8.1.1, 8.1.2 | Update status to SYSTEM\_DESIGN\_APPROVED or SYSTEM\_DESIGN\_REJECTED. |
| 8.2 | **ArchitectAgent Enhancement** |  |  |  |  |  |
| 8.2.1 | ArchitectAgent: Refine system design generation prompt (e.g., suggest key components, data stores, APIs based on PRD). | todo | high | low | 5.4.3 | Aim for a more structured output. |
| 8.3 | **HITL for Cost & Revenue Estimates** |  |  |  |  |  |
| 8.3.1 | Orchestrator: Update status flows for PLANNING\_COMPLETE\_PENDING\_REVIEW, COSTING\_COMPLETE\_PENDING\_REVIEW, REVENUE\_PENDING\_REVIEW. | todo | high | low | 6.1.3, 6.1.6, 6.2.3 | Define reviewers (e.g., initiator, sales manager). |
| 8.3.2 | BusinessCaseDetailPage.tsx: Allow editing of Effort Breakdown, Cost Estimate inputs (e.g., override rates, hours), Revenue Projection inputs. | todo | high | low | 6.3.1 | This might involve more complex forms. Backend APIs needed to save these overrides. |
| 8.3.3 | BusinessCaseDetailPage.tsx: Add "Submit for Approval" buttons for Cost & Revenue sections. | todo | high | low | 8.3.2 |  |
| 8.3.4 | Frontend: Show "Approve/Reject" buttons for Cost & Revenue for designated approvers. | todo | high | low | 7.3.3, 8.3.1, 8.3.3 | Update status for COSTING\_APPROVED, REVENUE\_APPROVED, etc. |
| 8.4 | **PlannerAgent, CostAnalystAgent, SalesValueAnalystAgent Enhancements** |  |  |  |  |  |
| 8.4.1 | PlannerAgent: More detailed effort estimation logic based on PRD/System Design features (e.g., simple keyword matching or complexity scoring). | todo | high | low | 6.1.3 |  |
| 8.4.2 | CostAnalystAgent: Use actual rates from selected/default rateCards in Firestore to calculate cost. | todo | high | low | 6.1.6, 7.1 (CRUD for Rate Cards) |  |
| 8.4.3 | SalesValueAnalystAgent: Use structure from selected/default pricingTemplates in Firestore for revenue calculation. | todo | high | low | 6.2.3, 7.2 (CRUD for Pricing Templates) |  |
| 8.5 | **FinancialModelAgent Implementation** |  |  |  |  |  |
| 8.5.1 | Create FinancialModelAgent stub (ADK agent structure). | todo | high | low | 2.1.2 | SDD Section 5\. |
| 8.5.2 | Orchestrator: Invoke FinancialModelAgent after Cost & Revenue are approved. | todo | high | low | 8.3.4 (statuses), 8.5.1 |  |
| 8.5.3 | FinancialModelAgent: Implement logic to combine approved Cost & Revenue figures, calculate basic metrics (e.g., ROI, Payback Period stub). | todo | high | low | 8.5.2 | Store in businessCases. Update status to FINANCIAL\_MODEL\_COMPLETE. |
| 8.5.4 | BusinessCaseDetailPage.tsx: Display Financial Model summary. | todo | high | low | 6.3.1, 8.5.3 |  |

---

**Phase 9: Final Approval Workflow, Export & Sharing**

* **Focus:** Implement the final business case approval workflow. Add functionality to export the business case as a PDF and generate a shareable link.  
* **Status:** All tasks todo.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 9.1 | **Final Approval Workflow** |  |  |  |  |  |
| 9.1.1 | Orchestrator/ApprovalAgent: Define logic for final approval chain (e.g., requires Sales Manager role if revenue \> X, or specific named approvers). | todo | high | low | 5.2.1, 7.3.1, 8.5.3 | Configurable approval rules (V1 can be simple, V2 more complex from Admin UI). |
| 9.1.2 | BusinessCaseDetailPage.tsx: Add "Submit for Final Approval" button when all sections are approved and financial model is complete. | todo | high | low | 8.5.3 (status) | Update status to PENDING\_FINAL\_APPROVAL. |
| 9.1.3 | Frontend: Show "Approve/Reject Final Business Case" buttons for designated final approvers. | todo | high | low | 7.3.3, 9.1.1, 9.1.2 | Update status to APPROVED or REJECTED\_FINAL. Log to auditLogs. |
| 9.1.4 | Admin UI: Basic interface to define/view simple approval rules (e.g., map case type/value to approver roles). | todo | medium | low | 6.4.1, 9.1.1 |  |
| 9.2 | **Export to PDF** |  |  |  |  |  |
| 9.2.1 | Backend: Implement a service/Cloud Function that takes caseId, fetches data from Firestore, and generates a PDF document. | todo | high | low | 2.3.1 (models) | Use a Python PDF generation library (e.g., ReportLab, WeasyPrint). |
| 9.2.2 | BusinessCaseDetailPage.tsx: Add "Export to PDF" button that calls the backend PDF generation service and triggers download. | todo | high | low | 9.2.1 |  |
| 9.3 | **Shareable Link** |  |  |  |  |  |
| 9.3.1 | Backend: Create a new type of read-only access token/mechanism for sharing. (Could be a signed URL to a specific view if simple enough). | todo | medium | low | 3.4.1 | For internal DrFirst use, maybe a simpler approach than public share tokens. |
| 9.3.2 | BusinessCaseDetailPage.tsx: Add "Generate Shareable Link" button. Link should provide a read-only view of the approved business case. | todo | medium | low | 9.3.1 | This might require a separate read-only view/route in the frontend that accepts the share token. |

---

**Phase 10: Browser Extension for Intake**

* **Focus:** Develop the Chrome/MS Edge browser extension to capture initial project ideas and send them to the backend to initiate a new business case.  
* **Status:** All tasks todo.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 10.1 | **Browser Extension Project Setup** |  |  |  |  |  |
| 10.1.1 | Create new project for browser extension (HTML, CSS, JavaScript/TypeScript) | todo | high | low | (Basic web dev knowledge) | Can use a simple bundler like Webpack or Parcel if TypeScript/React is used, or keep it vanilla JS for simplicity. SDD Section 4.1. |
| 10.1.2 | Define manifest.json for the extension (permissions: activeTab, storage, potentially access to specific DrFirst domains if scraping context) | todo | high | low | 10.1.1 | Permissions need to be carefully considered (least privilege). |
| 10.1.3 | Design basic UI for the extension popup (e.g., textarea for problem statement, optional fields for title, links to Confluence/Jira) | todo | high | low | 10.1.1 | Keep it very simple and focused. |
| 10.2 | **Extension Functionality** |  |  |  |  |  |
| 10.2.1 | Implement logic in popup.js to capture user input from the UI form | todo | high | low | 10.1.3 |  |
| 10.2.2 | Implement authentication flow for the extension (e.g., redirect to web app for login, then store a token securely in extension storage) | todo | high | low | 3.2 (Auth Service), 10.2.1 | This can be tricky. Simplest might be to require user to be logged into the main web app. Or use chrome.identity API if GCIP supports it for extensions. |
| 10.2.3 | Implement logic to make an authenticated API call from the extension to the backend /api/v1/initiate\_case\_from\_extension endpoint | todo | high | low | 3.4.2 (API Auth), 4.1.2 (Agent Service), 10.2.2 | New backend endpoint needed. This endpoint will take the extension's input and trigger the IntakeAgent flow. |
| 10.2.4 | Backend: Implement /api/v1/initiate\_case\_from\_extension endpoint to receive data, create a new case, and start the intake process | todo | high | low | 4.2.3 (Orchestrator intake) | Similar to how the web app initiates a case but tailored for extension input. |
| 10.2.5 | Extension: Provide feedback to the user (e.g., "Case created successfully\!" and optionally a link to the new case in the web app) | todo | medium | low | 10.2.3 |  |
| 10.2.6 | (Optional) Implement context scraping (e.g., selected text on page, current page URL) if defined in scope and permissions allow | todo | low | low | 10.1.2 | Requires content\_scripts in manifest and message passing. |
| 10.3 | **Packaging & Testing** |  |  |  |  |  |
| 10.3.1 | Test loading the extension locally in Chrome/Edge developer mode | todo | high | low | 10.1.1 |  |
| 10.3.2 | Package the extension for distribution (e.g., .zip file) | todo | medium | low | 10.1.1 | For internal DrFirst distribution, might not need public store submission immediately. |

---

**Phase 11: CI/CD Hardening & Full Setup**

* **Focus:** Ensure robust CI/CD pipelines for frontend, backend (Application Server & ADK Agents), and potentially the browser extension. Implement environment configurations.  
* **Status:** All tasks todo.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 11.1 | **CI/CD for Frontend (React App)** |  |  |  |  |  |
| 11.1.1 | Set up GitHub Actions (or DrFirst's preferred CI/CD tool) for the frontend repository | todo | highest | low | 3.1.1 | Assuming GitHub is used. |
| 11.1.2 | CI Pipeline: Implement steps for linting, running unit/integration tests, and building the React app | todo | highest | low | 3.1.3, (Test tasks from earlier phases) |  |
| 11.1.3 | CD Pipeline: Deploy built frontend assets to Firebase Hosting (or chosen static hosting) for dev, staging, prod environments | todo | high | low | 1.1.9 (Cloud Build/Artifact Reg), 11.1.2 | Environment-specific configurations (e.g., API endpoints). |
| 11.2 | **CI/CD for Backend (Application Server & ADK Agents on Cloud Run)** |  |  |  |  |  |
| 11.2.1 | Set up GitHub Actions for the backend repository | todo | highest | low | 2.2.1 |  |
| 11.2.2 | CI Pipeline: Implement steps for linting, running unit/integration tests, building Docker image for Application Server | todo | highest | low | 2.2.4, (Test tasks from earlier phases) |  |
| 11.2.3 | CD Pipeline: Push Docker image to Google Artifact Registry | todo | high | low | 1.1.9, 11.2.2 |  |
| 11.2.4 | CD Pipeline: Deploy new image version to Cloud Run for dev, staging, prod environments | todo | high | low | 2.2.5, 11.2.3 | Manage environment variables (DB connections, Vertex AI project, etc.) securely for each environment (e.g., via Secret Manager or Cloud Run env vars). |
| 11.3 | **Environment Configuration Management** |  |  |  |  |  |
| 11.3.1 | Define and manage environment-specific configurations for frontend (e.g., .env.development, .env.staging, .env.production) | todo | high | low | 3.2.1 | Ensure these are correctly used in CI/CD. |
| 11.3.2 | Define and manage environment-specific configurations for backend (Cloud Run environment variables, secrets from Secret Manager) | todo | high | low | 1.1.6, 11.2.4 |  |
| 11.4 | **Infrastructure as Code (IaC) \- Basic (Optional for V1)** |  |  |  |  |  |
| 11.4.1 | Evaluate using Terraform or Google Cloud Deployment Manager for defining core GCP resources (Firestore, GCS, Cloud Run services, API Gateway) | todo | low | low | (All Phase 1 tasks) | Highly recommended for maintainability but can be deferred if initial setup is manual. |
| 11.4.2 | Implement basic IaC scripts for key resources if chosen | todo | low | low | 11.4.1 |  |
| 11.5 | **CI/CD for Browser Extension (Optional for V1)** |  |  |  |  |  |
| 11.5.1 | Set up GitHub Actions for browser extension repository | todo | low | low | 10.1.1 |  |
| 11.5.2 | CI Pipeline: Linting, building/packaging the extension | todo | low | low | 10.3.2, 11.5.1 | Auto-publishing to stores is complex and likely out of scope for V1. |

---

**Phase 12: Advanced Features, Refinements & Iteration**

* **Focus:** Based on initial user feedback and V1 capabilities, implement advanced features like agent learning, deeper integrations, analytics, and general refinements. This phase is more theme-based than a strict sequence.  
* **Status:** All tasks todo.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 12.1 | **Agent Learning & Improvement (Iterative)** |  |  |  |  |  |
| 12.1.1 | Collect and analyze HITL feedback patterns (e.g., common edits to PRDs, system designs) | todo | medium | low | (Usage data from all HITL phases) | Manual analysis initially. |
| 12.1.2 | Refine agent prompts based on feedback analysis to improve draft quality | todo | medium | low | 12.1.1 | This is an ongoing activity. |
| 12.1.3 | (Advanced) Explore mechanisms for agents to learn from user edits (e.g., few-shot examples from successful edits, RAG with approved case data) | todo | low | high | (Requires significant data and MLOps infrastructure) | PRD V2 \- Future Consideration. Requires careful data governance within DrFirst. |
| 12.2 | **Deeper Integrations (Jira, Confluence, SharePoint)** |  |  |  |  |  |
| 12.2.1 | Design and implement bi-directional Jira integration (e.g., create Jira epic/stories from approved business case, pull status updates) | todo | medium | high | (Approved business cases), (Jira API knowledge) | PRD V2 \- Future Consideration. Requires secure API access to DrFirst Jira. |
| 12.2.2 | Design and implement Confluence integration (e.g., auto-create/update Confluence page with business case details) | todo | medium | medium | (Approved business cases), (Confluence API) | PRD V2 \- Future Consideration. |
| 12.3 | **Analytics & Reporting** |  |  |  |  |  |
| 12.3.1 | Implement basic analytics dashboard for Admins (e.g., number of cases created, approval times, common rejection reasons from auditLogs) | todo | medium | low | 2.3.3 (auditLogs), 6.4.1 | Can use Firestore queries and display in Admin UI or use Looker Studio. |
| 12.4 | **User Experience (UX) Refinements** |  |  |  |  |  |
| 12.4.1 | Conduct user feedback sessions and usability testing on V1/V1.x features | todo | high | low | (A deployed version of the app) |  |
| 12.4.2 | Iterate on UI/UX based on feedback (e.g., improve forms, streamline workflows, enhance AG-UI interactions) | todo | high | low | 12.4.1 | Ongoing process. |
| 12.5 | **Advanced MCP & A2A Communication** |  |  |  |  |  |
| 12.5.1 | Explore more advanced A2A protocols (e.g., negotiation if agents have conflicting suggestions, asynchronous event-driven communication via Pub/Sub) | todo | low | high | (Stable V1 agent ecosystem) | SDD Section 6.2, 10\. |
| 12.6 | **Support for Other Business Case Types (if prioritized)** |  |  |  |  |  |
| 12.6.1 | Analyze requirements for new business case types (e.g., marketing, infrastructure) | todo | low | medium | (Stakeholder input) | PRD V2 \- Future Consideration. |
| 12.6.2 | Adapt agent logic and UI to accommodate new types | todo | low | high | 12.6.1 |  |

