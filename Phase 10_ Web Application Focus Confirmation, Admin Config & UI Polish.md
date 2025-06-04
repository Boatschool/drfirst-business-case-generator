**Phase 10: Web Application Focus Confirmation, Admin Config & UI Polish**

* **Focus:** Confirm and solidify the web application as the sole primary interface by performing audit-driven cleanup. Implement basic admin configuration for final approvals. Then, polish the web application's usability, intake flow, and review initial deployment considerations.  
* **Prerequisite:** Task 10.0 (Codebase Audit for Web Application Focus) is COMPLETE, and its summary report is available.  
* **Status:** Audit cleanup tasks (10.0.1, 10.0.2) COMPLETE ✅. Remaining tasks todo unless otherwise specified.

| Task ID | Title | Status | Priority | Complexity | Dependencies | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **10.0.1** | **Execute Code & Script Cleanup based on Audit Report** | ✅ COMPLETE | highest | low | Task 10.0 (Audit Report) | **COMPLETED.** Commented out extension setup in scripts/setup\_dev\_env.sh. Moved browser-extension/ to archive/browser-extension/. Updated README.md structure. Git: feature/cleanup-audit-10.0.1 commit 2876432. |
| **10.0.2** | **Execute Documentation Cleanup based on Audit Report** | ✅ COMPLETE | highest | low | Task 10.0 (Audit Report) | **COMPLETED.** Updated README.md, SystemDesign.md, architecture diagrams, and DrFirst Bus Case \- Development Plan.md (Phase 10 section) to reflect web-first focus and remove extension references. Git: feature/cleanup-audit-10.0.1 commit 9f207d8. |
| **9.1.4** | **(Simplified V1) Implement Admin UI to Designate Global Final Approver Role** | todo | highest | medium | Task 10.0.1, 10.0.2, (Phases 1-7, 9.1.1-9.1.3 for backend approval logic) | **DEFERRED TASK.** Backend logic reads this config; Admin UI sets it. Involves Firestore systemConfiguration and admin UI changes. |
| **10.1** **Review and Refine Web Application Intake Flow** |  |  |  |  |  |  |
| 10.1.1 | Review the "New Business Case" creation flow (NewCasePage.tsx) for clarity, ease of use, and completeness. | todo | high | low | Task 4.4.3, 10.0.1, 10.0.2 | Ensure it's a smooth primary entry point. |
| 10.1.2 | Enhance NewCasePage.tsx with better user guidance or examples for "Problem Statement" and "Relevant Links". | todo | high | low | 10.1.1 | E.g., placeholder text, tooltips. |
| 10.1.3 | (Optional) Implement basic client-side validation for the New Case form (e.g., required fields, valid URL format for links). | todo | medium | low | 10.1.1 | Reduces backend errors and improves UX. |
| **10.2** **Dashboard and Navigation Enhancements** |  |  |  |  |  |  |
| 10.2.1 | Review DashboardPage.tsx: Improve case listing (e.g., add sorting, filtering by status, pagination for many cases). | todo | high | medium | Task 4.4.1 | As the number of cases grows, this becomes important. |
| 10.2.2 | Enhance main application navigation (e.g., in AppLayout.tsx): Ensure clear links to Dashboard, New Case, Admin (if admin role). | todo | high | low | Task 3.1.5, 6.4.1 | Make it easy for users to find key actions. |
| 10.2.3 | Implement consistent breadcrumbs or a clear page titling strategy for better user orientation. | todo | medium | low | (Overall frontend structure) | Especially for nested views like BusinessCaseDetailPage. |
| **10.3** **User Experience & UI Polish** |  |  |  |  |  |  |
| 10.3.1 | Conduct a general UI review across key pages for consistency in styling (MUI), terminology, and interaction patterns. | todo | medium | low | (All frontend pages) | Address any glaring inconsistencies. |
| 10.3.2 | Improve loading state indicators across the application (ensure they are clear and consistently used for API calls). | todo | medium | low | (All components making API calls) | E.g., skeleton loaders, consistent spinner placement. |
| 10.3.3 | Enhance error message display: Make error notifications user-friendly and provide actionable information where possible. | todo | medium | low | (All components handling API errors) | Instead of just "Error", something like "Failed to load cases. Please try again." |
| 10.3.4 | Review application for basic accessibility (a11y) considerations (e.g., keyboard navigation, sufficient color contrast, alt text stubs). | todo | low | medium | (All frontend pages) | This is a large topic, aim for basic improvements. |
| **10.4** **Deployment Configuration Review (Pre-CI/CD Hardening)** |  |  |  |  |  |  |
| 10.4.1 | Review and confirm environment variable setup for frontend (.env files for Vite) and backend (Cloud Run env vars/secrets). | todo | high | low | DEV\_LOG (Env Files), Task 11.3 (future) | Ensure all necessary configs are externalized and documented. |
| 10.4.2 | Verify CORS configuration on backend (FastAPI) is appropriate for the web app's deployed domain(s). | todo | high | low | DEV\_LOG (main.py, config.py) | Critical for deployed environments. |
| 10.4.3 | Review Firestore security rules: Ensure they are sufficiently granular. | todo | medium | medium | Task 1.1.3 (Firestore setup) | Review for production readiness; full implementation might be later. |
| 10.4.4 | Perform a manual test deployment of the current main branch to a dev or staging GCP environment. | todo | high | medium | Task 2.2.5 (initial Cloud Run), (Frontend deploy) | Dry run before full CI/CD automation. Update deployment scripts. |

---

