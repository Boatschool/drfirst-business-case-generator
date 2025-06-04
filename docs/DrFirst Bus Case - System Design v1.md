# **DrFirst Business Case Generator System Design V1**

## **1\. Introduction & Overview**

This document outlines the system design for the DrFirst Agentic Business Case Generator (Internal Codename: "Project Catalyst"). The system is an internally-focused, agent-powered platform designed to streamline the creation, refinement, and approval of business cases for software development projects within DrFirst.

It leverages a modular architecture built around specialized AI agents managed by an orchestrator. Communication between agents (Agent-to-Agent, A2A), between agents and the user interface (Agent-to-UI, AG-UI), and overall workflow management will adhere to principles of Multi-Party Coordination (MCP) to ensure coherent and efficient business case generation. The system will be hosted on Google Cloud Platform (GCP) and integrate with DrFirst's existing authentication mechanisms.

## **2\. Goals of the System Design**

* To define a scalable, maintainable, and secure architecture.  
* To detail the components, their interactions, and data flows.  
* To specify how agent protocols (A2A, AG-UI, MCP) will be implemented.  
* To outline data storage, AI model usage, and deployment on GCP.  
* To ensure alignment with DrFirst's technical standards and internal tool landscape (Jira, Confluence, SharePoint).

## **3\. High-Level Architecture**

The system follows a microservices-oriented approach where AI agents act as specialized services.

     graph TD  
    subgraph User Layer  
        WebAppUI\[Web Application UI (React \- Complete Interface)\] \--\> API\_GW  
    end

    subgraph GCP Backend  
        API\_GW\[API Gateway\] \--\> AppServer\[Application Server (Cloud Run \- ADK based)\]

        subgraph AppServer  
            OrchestratorAgent\[Orchestrator Agent (MCP Core)\]  
            AuthService\[Authentication Service (DrFirst SSO Integration)\]  
            HITL\_Manager\[HITL Management Module\]  
            ConfigService\[Configuration Service\]  
            ExportService\[Export/Link Service\]

            OrchestratorAgent \--\> AgentPool\[Specialized Agent Pool\]  
            OrchestratorAgent \--- HITL\_Manager  
            ConfigService \--- FirestoreDB\[(Firestore: RateCards, Templates)\]  
            AuthService \--- IdentityPlatform\[Google Identity Platform / DrFirst SSO\]  
        end

        subgraph AgentPool  
            PMA\[Product Manager Agent\]  
            ArchitectA\[Architect Agent\]  
            PlannerA\[Planner Agent\]  
            AnalystA\[Cost Analyst Agent\]  
            SalesAnalystA\[Sales/Value Analyst Agent\]  
            FinancialModelA\[Financial Model Agent\]  
            ApprovalA\[Approval Agent\]  
        end

        AppServer \--\> VertexAI\[Vertex AI (LLMs)\]  
        AppServer \--\> FirestoreDB  
        AgentPool \--\> VertexAI  
        AgentPool \-- A2A via Orchestrator/Firestore \--\> AgentPool

        FirestoreDB \-- Stores \--\> BusinessCases\[Business Cases Data\]  
        FirestoreDB \-- Stores \--\> UserData\[User Data & Roles\]

        WebAppUI \-- AG-UI Interactions \--\> AppServer  
    end

    subgraph DrFirst Ecosystem (Future Deeper Integrations)  
        Jira\[DrFirst Jira\]  
        Confluence\[DrFirst Confluence\]  
        SharePoint\[DrFirst SharePoint\]  
    end

    AppServer \-.-\>|Initial Context/Links| DrFirstEcosystem  
    AppServer \-.-\>|Future API Integrations| DrFirstEcosystem  
   

**Key Architectural Principles:**

* **Modularity:** Specialized agents for distinct tasks.  
* **Orchestration:** Central orchestrator\_agent manages workflow and agent coordination.  
* **Stateless Agents (Mostly):** Individual content-generating agents can be largely stateless, receiving context and producing output. The orchestrator\_agent and HITL\_Manager will manage state.  
* **Event-Driven Considerations:** While not fully event-driven in V1, the design allows for future evolution towards more asynchronous, event-driven A2A communication (e.g., using Pub/Sub).

## **4\. Components**

### **4.1. Frontend Components**

\*   \*\*Web Application UI:\*\*  
    \*   \*\*Technology:\*\* React with TypeScript and Material-UI for comprehensive user experience.  
    \*   \*\*Functionality:\*\*  
        \*   Complete business case intake and creation workflow.  
        \*   Dashboard for viewing and managing business cases.  
        \*   Conversational interface for guided input and agent interaction.  
        \*   Document editor for reviewing and modifying agent-generated content (PRD, System Design, etc.).  
        \*   HITL review and approval workflows.  
        \*   Admin panel for managing users, rate cards, pricing templates, approval rules.  
        \*   PDF export and sharing capabilities.  
    \*   \*\*AG-UI:\*\* Rich interaction with the backend. Displays agent outputs, collects user feedback/edits, triggers agent revisions, and manages approval steps.  
     
IGNORE\_WHEN\_COPYING\_START  
content\_copy download  
Use code [with caution](https://support.google.com/legal/answer/13505487).  
IGNORE\_WHEN\_COPYING\_END

### **4.2. Backend Components (Hosted on GCP Cloud Run)**

     \*   \*\*API Gateway (Google Cloud API Gateway):\*\*  
    \*   Manages external access to backend services, handles routing, authentication (via AuthService), rate limiting, CORS.  
\*   \*\*Application Server (Google Agent Developer Kit \- ADK):\*\*  
    \*   The core application runtime built using Python and ADK.  
    \*   \*\*Authentication Service:\*\* Integrates with DrFirst's SSO solution (e.g., SAML/OIDC via Google Identity Platform) to authenticate users and fetch roles.  
    \*   \*\*\`orchestrator\_agent\`:\*\*  
        \*   The heart of the MCP implementation.  
        \*   Manages the end-to-end business case generation lifecycle (state machine).  
        \*   Invokes specialized agents in sequence or parallel where appropriate.  
        \*   Handles A2A communication logic (e.g., passing outputs of one agent as inputs to another, potentially using Firestore as an intermediary blackboard).  
        \*   Coordinates with the \`HITL\_Manager\`.  
    \*   \*\*Specialized Agent Pool:\*\* Individual agents built with ADK/Langchain, each responsible for a specific task (see section 5).  
    \*   \*\*HITL Management Module:\*\*  
        \*   Pauses workflows pending human review.  
        \*   Receives and stores user feedback/edits from the UI.  
        \*   Notifies the \`orchestrator\_agent\` when a review step is complete.  
    \*   \*\*Configuration Service:\*\* Provides APIs for Admins (via WebAppUI) to manage rate cards, pricing templates, and approval workflows stored in Firestore.  
    \*   \*\*Export Service:\*\* Generates PDF versions of business cases and secure shareable links.  
     
IGNORE\_WHEN\_COPYING\_START  
content\_copy download  
Use code [with caution](https://support.google.com/legal/answer/13505487).  
IGNORE\_WHEN\_COPYING\_END

### **4.3. AI Services**

     \*   \*\*Vertex AI:\*\*  
    \*   Provides access to Google's foundation LLMs (e.g., Gemini) for all generative tasks performed by the agents.  
    \*   Agents will construct prompts, send them to Vertex AI, and process the responses.  
     
IGNORE\_WHEN\_COPYING\_START  
content\_copy download  
Use code [with caution](https://support.google.com/legal/answer/13505487).  
IGNORE\_WHEN\_COPYING\_END

### **4.4. Data Stores**

     \*   \*\*Firestore (NoSQL Document Database):\*\*  
    \*   \*\*\`businessCases\` collection:\*\* Stores all data related to a business case (ID, status, user inputs, agent-generated content drafts, HITL feedback, approval history, links to Confluence/SharePoint, etc.).  
    \*   \*\*\`users\` collection:\*\* DrFirst user profiles, system roles, preferences.  
    \*   \*\*\`rateCards\` collection:\*\* Admin-managed rate cards for cost estimation.  
    \*   \*\*\`pricingTemplates\` collection:\*\* Admin-managed templates for revenue/value projection.  
    \*   \*\*\`auditLogs\` collection:\*\* Records key agent actions, user modifications, and approval steps for MCP traceability.  
     
IGNORE\_WHEN\_COPYING\_START  
content\_copy download  
Use code [with caution](https://support.google.com/legal/answer/13505487).  
IGNORE\_WHEN\_COPYING\_END

## **5\. Agent Roles and Responsibilities**

Each agent is a specialized module, likely a Python class/function set within the ADK framework.

| Agent | Responsibility | Key Inputs | Key Outputs | A2A Interactions (Examples) |
| :---- | :---- | :---- | :---- | :---- |
| orchestrator\_agent | Manages workflow, state, A2A, HITL handoffs, MCP. | User request, agent outputs, HITL feedback | Instructions to agents, status updates | Invokes all other agents, manages data flow |
| intake\_agent | (Part of conversational UI/Orchestrator) Guides user through initial project definition. | User's initial idea | Structured project brief/requirements | Feeds product\_manager\_agent |
| product\_manager\_agent | Writes the PRD draft. | Structured project brief, Confluence/Jira links | PRD document (Markdown/JSON) | Consumes output from intake\_agent |
| architect\_agent | Generates system design options/recommendations. | Approved PRD | System Design document (Markdown/JSON) | Consumes PRD from product\_manager\_agent |
| planner\_agent | Estimates development effort by role based on PRD and System Design. | Approved PRD, System Design | Effort breakdown (e.g., role-hours) | Consumes PRD & System Design |
| cost\_analyst\_agent | Applies rate card to effort breakdown to generate cost estimate. | Effort breakdown, Rate Card | Cost estimate document | Consumes planner\_agent output |
| sales\_value\_analyst\_agent | Calculates revenue/value scenarios based on PRD and pricing/value templates. | Approved PRD, Pricing/Value Templates | Revenue/Value forecast (low/base/high) | Consumes PRD |
| financial\_model\_agent | Combines cost estimate and revenue/value forecast into a consolidated financial view (ROI, payback etc.). | Cost estimate, Revenue/Value forecast | Financial summary/model | Consumes outputs from cost\_analyst & sales\_value\_analyst |
| approval\_agent | Handles routing of the business case for approval based on defined workflows and user permissions. | Completed Business Case, Approval Rules | Approval requests, status updates | Triggered by orchestrator\_agent |
| document\_retrieval\_agent | (Future/Advanced) Retrieves relevant information from linked **Confluence/SharePoint/Jira** to enrich context. | URLs, search queries | Summarized text, relevant snippets | Provides context to other generative agents |

## **6\. Communication Protocols & Coordination**

### **6.1. Agent-to-UI (AG-UI)**

* **Mechanism:** RESTful APIs exposed by the Application Server and consumed by the Web Application UI.  
* **Interaction:**  
  * UI sends user inputs/commands (e.g., start new case, submit feedback, approve).  
  * Backend sends agent-generated content, status updates, and requests for HITL.  
  * UI clearly distinguishes AI-generated content and provides tools for interaction.

### **6.2. Agent-to-Agent (A2A)**

* **Mechanism (V1):** Primarily orchestrated. The orchestrator\_agent calls specialized agents sequentially or in a defined order, passing data directly or via temporary storage in Firestore (acting as a "blackboard").  
  * *Example:* product\_manager\_agent output (PRD stored in Firestore) is an input for architect\_agent.  
* **Data Format:** Standardized JSON structures for inter-agent data exchange.  
* **Future Evolution:** Could involve asynchronous messaging (e.g., Google Pub/Sub) for more decoupled and scalable A2A, especially if agents become more independent services.

### **6.3. Multi-Party Coordination (MCP)**

* **Core Implementation:** The orchestrator\_agent acts as the central coordinator.  
* **State Management:** Business case status and artifact versions are tracked in Firestore.  
* **Workflow Definition:** Approval workflows and agent sequences are configurable (managed by Admins).  
* **Dependency Management:** The orchestrator ensures that agents are invoked only when their prerequisite inputs are available and approved (e.g., System Design agent runs after PRD is reviewed).  
* **Concurrency and Locking (Simplified for V1):** For V1, assume one primary "editor" or agent working on a section at a time to avoid complex merge conflicts. Firestore transactions can be used for atomic updates.  
* **Auditability:** All significant actions by agents and users are logged in the auditLogs collection.

## **7\. Data Models (Firestore Collections \- Key Fields)**

* **businessCases:**  
  * caseId (PK), title, status (e.g., DRAFT, PENDING\_PRD\_REVIEW, PENDING\_TECH\_REVIEW, PENDING\_FINAL\_APPROVAL, APPROVED, REJECTED), initiatorId (FK to users), createdAt, updatedAt, prdV1 (JSON/Markdown), prdFeedbackV1, systemDesignV1, costModelIdV1, currentEditorId, linkedConfluencePages (array of strings), linkedJiraIssues (array of strings), approvalHistory (array of objects: { approverId, role, decision, comments, timestamp }).  
* **users:**  
  * userId (PK, DrFirst Employee ID), email, displayName, drFirstRoles (array of strings), systemRole (e.g., ADMIN, BUSINESS\_USER, DEVELOPER).  
* **rateCards:**  
  * cardId (PK), name, isActive, default, roles (array of objects: {roleName, hourlyRate, currency}).  
* **pricingTemplates:**  
  * templateId (PK), name, description, structureDefinition (JSON defining calculation logic).  
* **auditLogs:**  
  * logId (PK), caseId (FK), timestamp, actorType (USER or AGENT), actorId, actionDescription, details (JSON blob).

## **8\. Deployment on GCP**

* **Frontend (Web Application UI):**  
  * React: Firebase Hosting (static assets) or Google Cloud Storage with CDN for static hosting.  
* **Backend (Application Server \- ADK based):** Cloud Run (containerized Python application).  
* **API Gateway:** Google Cloud API Gateway.  
* **Database:** Firestore.  
* **AI Services:** Vertex AI.  
* **Authentication:** Google Identity Platform, configured to federate with DrFirst's SSO provider.  
* **Logging & Monitoring:** Google Cloud Logging and Cloud Monitoring.  
* **CI/CD:** Cloud Build and Artifact Registry for building and storing container images.

## **9\. Security Considerations**

* **Authentication:** Integration with DrFirst's SSO (e.g., Okta, Azure AD via Google Identity Platform).  
* **Authorization:** RBAC enforced at the API Gateway and Application Server level based on DrFirst roles mapped to system roles.  
* **Data Encryption:**  
  * In Transit: HTTPS for all communications.  
  * At Rest: Firestore default encryption. CMEK if required by DrFirst policy.  
* **Input Sanitization:** To prevent injection attacks, especially for LLM prompts.  
* **Secrets Management:** Google Secret Manager for API keys, database credentials.  
* **Vulnerability Scanning:** Regular scanning of container images and dependencies.  
* **Compliance:** Adherence to DrFirst data security policies and relevant regulations (e.g., HIPAA considerations if any PHI-like data, even if anonymized, could be inferred or is part of the input).  
* **A2A Security:** As all agents run within the trusted GCP environment controlled by DrFirst, inter-agent communication risks are lower but should still use authenticated internal endpoints if agents are ever deployed as separate Cloud Run services.

## **10\. Future Considerations / Scalability**

* **Deeper Jira/Confluence/SharePoint Integration:** Bi-directional data flow (e.g., create Jira tickets, update Confluence pages).  
* **Advanced Agent Capabilities:** Agents that learn from HITL feedback (requires careful governance of data used for fine-tuning).  
* **Event-Driven A2A:** Using Pub/Sub for more robust and scalable asynchronous agent communication.  
* **Enhanced MCP:** More sophisticated conflict resolution, negotiation protocols between agents.  
* **Analytics & Reporting:** Dashboards on business case velocity, approval rates, common bottlenecks.

