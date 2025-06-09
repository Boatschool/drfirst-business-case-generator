# Current Firestore Security Rules Analysis

## Overview

This document analyzes the existing Firestore security rules for the DrFirst Agentic Business Case Generator to identify overly permissive patterns and security vulnerabilities before production deployment.

## Current Rules Structure

The existing `config/firebase/firestore.rules` file contains:
- Helper functions for role checking and authentication
- Collection-specific rules for users, businessCases, admin collections
- Default deny-all fallback rule

## Security Analysis

### ✅ **Strengths Identified**

1. **Well-structured helper functions**
   - `getUserRole()` with fallback strategy from custom claims to Firestore
   - Proper authentication checks (`isAuthenticated()`)
   - Role-based helper functions (`isAdmin()`, `hasRole()`)

2. **Default deny principle**
   - Explicit `allow read, write: if false;` for unmatched documents
   - Audit logs collection properly locked down

3. **Basic access controls**
   - Users can only read their own documents
   - Admin override capabilities

### ⚠️ **Security Concerns & Overly Permissive Rules**

#### 1. **Business Cases Collection - Overly Broad Read Access**

**Current Rule Issue:**
```javascript
allow read: if isAuthenticated() && 
               (isOwner(resource.data.user_id) ||
                isAdmin() ||
                (resource.data.status == 'CASE_APPROVED') ||
                (resource.data.status == 'PENDING_FINAL_APPROVAL') ||
                // ... multiple status-based conditions
```

**Problems:**
- **ANY authenticated user can read APPROVED cases** - This may expose sensitive business information
- **PENDING_FINAL_APPROVAL cases readable by all** - Should be restricted to final approvers only
- **Missing role-based restrictions** for stage-specific statuses

#### 2. **Missing Evaluation Collections**

**Gap:** The rules don't cover essential evaluation collections:
- `humanEvaluationResults`
- `automatedEvaluationResults` 
- `automatedEvaluationRuns`

**Risk:** These collections would fall through to the default deny rule, but they should have explicit admin-only access rules.

#### 3. **Missing Agent Prompts Collection**

**Gap:** No rules for `agentPrompts` collection mentioned in requirements.

#### 4. **Admin Collections - Too Simplistic**

**Current Rule:**
```javascript
match /rateCards/{cardId} {
  allow read, write: if isAdmin();
}
```

**Issues:**
- **No read access for regular users** who might need pricing information for case creation
- **Should differentiate read vs write permissions** (users might need read access)

#### 5. **Business Case Update Rules - Potential Race Conditions**

**Current Rule:**
```javascript
allow update: if isAuthenticated() && 
                 (isAdmin() ||
                  (isOwner(resource.data.user_id) && 
                   (!request.resource.data.diff(resource.data).affectedKeys().hasAny(['status', 'user_id', 'created_at']))));
```

**Issues:**
- **No validation of status transitions** - owners can update cases in any status
- **Missing workflow state validation** - should restrict updates based on current workflow stage
- **No concurrent modification protection**

#### 6. **Role-based Access Not Granular Enough**

**Current Issues:**
- **Developers can read System Design cases** but rules don't validate if they're assigned as approvers
- **No stage-specific approver validation** based on system configuration
- **Finance/Legal approvers not properly integrated** into business case access patterns

#### 7. **Jobs Collection - Incomplete Implementation**

**Current Rule:**
```javascript
match /jobs/{jobId} {
  allow read: if isAuthenticated() && 
                 resource.data.user_id == request.auth.uid;
  allow write: if false;
}
```

**Issues:**
- **Backend service accounts can't write** - needs service account detection
- **No job status-based access controls**

## Missing Collection Rules

The following collections need explicit security rules:

1. **`humanEvaluationResults`** - Admin and evaluator access only
2. **`automatedEvaluationResults`** - Admin read-only, backend write-only  
3. **`automatedEvaluationRuns`** - Admin read-only, backend write-only
4. **`agentPrompts`** - Admin-only access for prompt management

## Compliance Issues

### **Principle of Least Privilege Violations**

1. **Over-broad read access** to approved business cases
2. **Missing role-based restrictions** for workflow stages
3. **Admin collections** should allow read access for legitimate business users

### **Production Readiness Concerns**

1. **Sensitive business data exposure** through approved case sharing
2. **No audit trail** for rule-based access decisions
3. **Missing input validation** on critical fields during updates
4. **No rate limiting** or abuse prevention mechanisms

## Recommendations Summary

1. **Implement granular status-based access** with proper role validation
2. **Add explicit rules for all evaluation collections**
3. **Differentiate read/write permissions** for admin collections
4. **Add workflow state validation** for business case updates
5. **Implement stage-specific approver validation**
6. **Add service account detection** for backend operations
7. **Strengthen input validation** and concurrent modification protection

## Risk Assessment

| Risk Level | Category | Impact |
|------------|----------|---------|
| **HIGH** | Business Case Data Exposure | Sensitive financial/strategic information accessible to all authenticated users |
| **MEDIUM** | Missing Collection Rules | Evaluation data falls to default deny, blocking legitimate access |
| **MEDIUM** | Insufficient Role Validation | Users might access cases outside their approval authority |
| **LOW** | Admin Collection Access | Pricing data might be needed by users for case creation |

## Next Steps

1. Implement proposed granular security rules
2. Test rules with Firestore Emulator
3. Validate role-based access patterns
4. Deploy to staging for integration testing 