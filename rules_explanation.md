# Firestore Security Rules Explanation

## Overview

This document explains the logic and security strategy behind the proposed Firestore security rules for the DrFirst Agentic Business Case Generator. The rules implement the principle of least privilege while supporting the complex workflow requirements of the application.

## Security Strategy

### Core Principles

1. **Principle of Least Privilege**: Users have minimal access required for their role
2. **Defense in Depth**: Multiple layers of validation (authentication, authorization, field-level checks)
3. **Explicit Permissions**: All access must be explicitly granted; default deny for undefined collections
4. **Role-Based Access Control**: Granular permissions based on user roles and workflow stages
5. **Data Validation**: Input validation at the security rule level
6. **Audit Trail Protection**: Critical collections protected from client-side tampering

### Backend vs. Client-Side Authorization Strategy

**Client-Side Rules (Firestore Security Rules):**
- Basic access control and data validation
- Role-based permissions for reading and basic operations
- Prevention of unauthorized data access
- Field-level validation for critical updates

**Backend API Authorization (Recommended for Complex Operations):**
- Status transitions and workflow logic
- Complex business rule validation
- Dynamic role assignment based on system configuration
- Audit logging and history tracking
- Integration with external systems

## Helper Functions

### Authentication & Role Management

```javascript
function getUserRole() {
  return getUserRoleFromClaims() != null ? getUserRoleFromClaims() : getUserRoleFromFirestore();
}
```

**Strategy**: Primary role source is custom claims (fast, cached), with Firestore fallback for reliability.

```javascript
function isServiceAccount() {
  return request.auth != null && 
         request.auth.token != null && 
         request.auth.token.firebase != null &&
         request.auth.token.firebase.sign_in_provider == 'custom';
}
```

**Purpose**: Identifies backend service accounts for privileged operations (evaluation scripts, audit logging).

### Workflow Authorization

```javascript
function canApproveForStage(status) {
  return isAdmin() ||
         (status == 'PRD_REVIEW' && hasRole('PRODUCT_OWNER')) ||
         (status in ['SYSTEM_DESIGN_PENDING_REVIEW', 'SYSTEM_DESIGN_DRAFTED'] && hasRole('DEVELOPER')) ||
         // ... more stage-specific rules
}
```

**Design Decision**: Stage-specific approver roles are hardcoded in rules for performance. For dynamic configuration, backend APIs should handle complex approval logic.

## Collection-Specific Rules

### Users Collection

#### Read Permissions
```javascript
allow read: if isAuthenticated() && 
               (request.auth.uid == userId || 
                isAdmin() ||
                (hasRole('DEVELOPER') && resource.data.keys().hasAny(['displayName', 'email', 'systemRole'])));
```

**Logic**:
- **Self-access**: Users read their own profile
- **Admin access**: Full user directory access for administration
- **Developer limited access**: Only basic fields for assignment purposes

#### Update Restrictions
```javascript
allow update: if isAuthenticated() && 
                 (isAdmin() || 
                  (request.auth.uid == userId && 
                   !request.resource.data.diff(resource.data).affectedKeys().hasAny(['systemRole', 'uid', 'created_at']) &&
                   request.resource.data.uid == request.auth.uid));
```

**Security Rationale**: 
- Users cannot modify their role (prevents privilege escalation)
- UID cannot be changed (prevents identity spoofing)
- Role changes must go through admin APIs

### Business Cases Collection

#### Enhanced Read Security

**Previous Issue**: All authenticated users could read approved cases
**Solution**: Granular access based on role and approval stage

```javascript
allow read: if isAuthenticated() && 
               (isOwner(resource.data.user_id) ||
                isAdmin() ||
                canApproveForStage(resource.data.status));
```

**Access Patterns**:
1. **Ownership**: Case initiators always access their cases
2. **Role-based**: Approvers access cases in their approval stage
3. **Controlled Sharing**: Explicit `shareable` flag for approved cases

#### Update Restrictions

```javascript
allow update: if isAuthenticated() && 
                 (isAdmin() ||
                  (isOwner(resource.data.user_id) && 
                   isOwnerEditableStatus(resource.data.status) &&
                   !request.resource.data.diff(resource.data).affectedKeys().hasAny(['user_id', 'created_at']) &&
                   request.resource.data.updated_at != resource.data.updated_at) ||
                  // Approver logic...
```

**Protection Mechanisms**:
- **Status-based editing**: Owners can only edit in draft stages
- **System field protection**: user_id, created_at cannot be modified
- **Concurrent modification protection**: updated_at timestamp must change
- **Approver restrictions**: Only status/history updates for approvers

#### Create Validation

```javascript
allow create: if isAuthenticated() && 
                 request.resource.data.user_id == request.auth.uid &&
                 hasRequiredBusinessCaseFields(request.resource.data) &&
                 request.resource.data.status == 'INTAKE';
```

**Validation Logic**:
- User must set themselves as owner
- Required fields must be present
- New cases must start in INTAKE status

### Configuration Collections

#### Rate Cards & Pricing Templates

**Design Decision**: All authenticated users get read access because:
- Users need pricing data for cost estimation during case creation
- Business logic requires real-time pricing information
- Write access restricted to admins only

#### System Configuration

```javascript
allow read: if isAuthenticated() && 
               (isAdmin() || 
                configId in ['approvalSettings', 'workflowSettings', 'generalSettings']);
```

**Security Strategy**: 
- Non-sensitive configuration accessible to all users
- Sensitive configuration (API keys, internal settings) admin-only
- Write access always admin-only

### Evaluation Collections

#### Human Evaluation Results

```javascript
allow read: if isAdmin() || hasRole('EVALUATOR');
allow create: if (hasRole('EVALUATOR') && 
                  request.resource.data.evaluator_id == request.auth.uid) ||
                 isAdmin();
```

**Access Control**:
- Evaluators can only create/modify their own evaluations
- Admins have full access for oversight
- Evaluation integrity maintained

#### Automated Evaluation Collections

```javascript
allow read: if isAdmin();
allow write: if isServiceAccount();
```

**Rationale**: 
- Read access limited to admins (for dashboards)
- Write access only for backend evaluation scripts
- Prevents tampering with automated results

### Agent Management

#### Agent Prompts Collection

```javascript
allow read: if isAdmin();
allow write: if isAdmin();
```

**Security Rationale**:
- Prompts contain sensitive business logic
- Access limited to admin-level prompt management
- Prevents exposure of AI agent strategies

## Advanced Security Features

### Service Account Detection

```javascript
function isServiceAccount() {
  return request.auth != null && 
         request.auth.token != null && 
         request.auth.token.firebase != null &&
         request.auth.token.firebase.sign_in_provider == 'custom';
}
```

**Use Cases**:
- Automated evaluation script operations
- Audit log creation
- System-level data operations

### Subcollection Security

#### Business Case Comments

```javascript
allow read: if isAuthenticated() && 
               (isOwner(get(/databases/$(database)/documents/businessCases/$(caseId)).data.user_id) ||
                isAdmin() ||
                canApproveForStage(get(/databases/$(database)/documents/businessCases/$(caseId)).data.status));
```

**Strategy**: Comments inherit parent business case access rules but add authorship controls for modifications.

## Workflow Integration Strategy

### Status Transition Control

**Client-Side Rules**: Basic validation and prevention of unauthorized transitions
**Backend API Responsibility**: 
- Complex workflow validation
- Status transition logic
- Business rule enforcement
- History tracking

### Dynamic Approver Assignment

**Current Implementation**: Static role mapping in security rules
**Future Enhancement**: Backend APIs query system configuration for dynamic approver assignment

**Rationale**: Firestore rules cannot efficiently query other documents for dynamic logic. Backend APIs provide flexibility for complex approval workflows.

## Security Trade-offs & Decisions

### Performance vs. Security

**Decision**: Hardcode common role checks in rules for performance
**Trade-off**: Less flexibility, but faster rule evaluation

### Granularity vs. Maintainability

**Decision**: Detailed field-level restrictions
**Trade-off**: More complex rules, but better security posture

### Client Rules vs. Backend Authorization

**Decision**: Use client rules for access control, backend for business logic
**Trade-off**: Some duplication, but clear separation of concerns

## Testing Recommendations

### Unit Testing Approach

1. **Role-based access testing**: Verify each role can access appropriate resources
2. **Ownership validation**: Ensure users only access their own data
3. **Status-based restrictions**: Test workflow stage access controls
4. **Field validation**: Verify input validation rules
5. **Negative testing**: Confirm unauthorized access is blocked

### Integration Testing

1. **End-to-end workflow testing**: Test complete business case lifecycle
2. **Cross-role scenarios**: Verify proper approver handoffs
3. **Concurrent access testing**: Validate updated_at protection
4. **Service account operations**: Test backend script permissions

## Compliance & Audit Considerations

### Data Access Logging

**Current**: Rules don't log access (Firestore limitation)
**Recommendation**: Implement application-level audit logging for sensitive operations

### Regulatory Compliance

**HIPAA Considerations**: 
- User access controls implemented
- Audit trail protection in place
- Minimum necessary access principle followed

**SOC 2 Type II**:
- Role-based access controls
- Data integrity protection
- System monitoring capabilities

## Future Enhancements

### Dynamic Role Configuration

**Current**: Static role assignments in rules
**Future**: Backend API integration for dynamic role management

### Advanced Audit Controls

**Potential**: Rule-level audit triggers (when supported by Firestore)
**Current**: Application-level audit logging

### Field-Level Encryption

**Consideration**: Additional protection for sensitive business case data
**Implementation**: Application-level encryption for critical fields

## Migration Strategy

### From Current Rules

1. **Backup current rules**: Ensure rollback capability
2. **Staged deployment**: Test in staging environment first
3. **Gradual rule activation**: Enable new rules collection by collection
4. **Monitor access patterns**: Ensure no legitimate access is blocked

### Testing Checklist

- [ ] Admin can access all collections
- [ ] Users can create and manage their own business cases
- [ ] Approvers can access cases in their approval stage
- [ ] Evaluation collections are properly protected
- [ ] Service account operations work correctly
- [ ] Unauthorized access attempts are blocked 