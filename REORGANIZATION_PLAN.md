# Codebase Reorganization Plan

## Overview
This document outlines the reorganization plan for the DrFirst Business Case Generator codebase to improve maintainability, discoverability, and development workflow.

## Current Issues

### 1. Root Directory Clutter
- Multiple implementation summary files scattered in root
- E2E test files mixed with application code
- Configuration files not grouped logically

### 2. Documentation Organization
- Implementation summaries scattered between root and docs/
- Mixed documentation types in same directories
- No clear hierarchy for different doc types

### 3. Test Organization
- E2E tests in root instead of tests/ directory
- Backend tests well-organized but isolated
- No unified test configuration

### 4. Build/Deploy Artifacts
- Temporary directories committed to repo
- Build artifacts mixed with source code

## Proposed Structure

```
drfirst-business-case-generator/
├── .github/                          # GitHub workflows and templates
├── .vscode/                          # VS Code settings (if used)
├── backend/                          # Backend application
│   ├── app/                         # FastAPI application
│   ├── tests/                       # Backend tests
│   ├── scripts/                     # Backend-specific scripts
│   └── docs/                        # Backend-specific documentation
├── frontend/                         # Frontend application
│   ├── src/                         # React/Vue source code
│   ├── tests/                       # Frontend tests
│   ├── scripts/                     # Frontend-specific scripts
│   └── docs/                        # Frontend-specific documentation
├── shared/                           # Shared code and types
├── docs/                             # Project documentation
│   ├── architecture/                # System design, ADRs
│   ├── deployment/                  # Deployment guides
│   ├── development/                 # Development setup, guides
│   ├── implementation/              # Implementation summaries
│   ├── testing/                     # Testing guides
│   ├── user/                        # User guides, manuals
│   └── reports/                     # Evaluation reports, analysis
├── tests/                            # Cross-component tests
│   ├── e2e/                         # End-to-end tests
│   ├── integration/                 # Integration tests
│   └── manual/                      # Manual test procedures
├── scripts/                          # Project-wide scripts
│   ├── deployment/                  # Deployment automation
│   ├── testing/                     # Test automation
│   ├── maintenance/                 # Maintenance scripts
│   └── development/                 # Development helpers
├── config/                           # Configuration files
│   ├── docker/                      # Docker configurations
│   ├── firebase/                    # Firebase configurations
│   └── environments/                # Environment-specific configs
├── tools/                            # Development tools and utilities
└── README.md                         # Main project documentation
```

## Migration Steps

### Phase 1: Create New Directory Structure
1. Create new directories following the proposed structure
2. Set up proper .gitignore patterns
3. Create index files for major sections

### Phase 2: Move Implementation Summaries
Move all `*_IMPLEMENTATION_SUMMARY.md` files to `docs/implementation/`

### Phase 3: Move E2E Tests
Consolidate E2E test files into `tests/e2e/`

### Phase 4: Organize Documentation
- Move technical docs to appropriate subdirectories
- Create clear README files for each section
- Establish documentation standards

### Phase 5: Clean Up Root Directory
- Remove temporary directories
- Organize configuration files
- Update references in all files

### Phase 6: Update Build/Deploy Scripts
- Update all script references
- Fix import paths
- Update CI/CD configurations

## Benefits of Reorganization

1. **Improved Discoverability**: Clear hierarchy makes finding files easier
2. **Better Separation of Concerns**: Related files grouped together
3. **Cleaner Root Directory**: Essential files only at top level
4. **Standardized Structure**: Consistent organization across project
5. **Better Maintainability**: Easier to update and maintain
6. **Enhanced Collaboration**: Team members can navigate more easily

## Implementation Timeline

- **Week 1**: Phase 1-2 (Structure + Implementation docs)
- **Week 2**: Phase 3-4 (Tests + Documentation)
- **Week 3**: Phase 5-6 (Cleanup + Updates)

## Rollback Plan

All changes will be made in a feature branch with:
- Complete file history preservation
- Comprehensive testing before merge
- Detailed migration documentation
- Quick rollback procedures if needed 