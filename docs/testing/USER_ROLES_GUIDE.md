# DrFirst Business Case Generator - User Roles Guide

## 🎯 Overview

The DrFirst Business Case Generator implements a comprehensive role-based access control (RBAC) system that enables fine-grained permissions for different user types throughout the business case lifecycle.

## 📋 Available Roles

| Role | Code | Description | Key Permissions |
|------|------|-------------|-----------------|
| 🔑 **System Administrator** | `ADMIN` | Full system access | All permissions, user management, system configuration |
| 👤 **Regular User** | `USER` | Standard user access | Create and manage own business cases |
| 👁️ **View-Only User** | `VIEWER` | Read-only access | View business cases (limited scope) |
| 👨‍💻 **Developer** | `DEVELOPER` | Technical reviewer | Approve/reject system designs, technical reviews |
| 💼 **Sales Representative** | `SALES_REP` | Sales team member | Create sales-focused business cases, initial value projections |
| 📊 **Sales Manager** | `SALES_MANAGER` | Sales leadership | Approve sales projections, revenue estimates, manage sales team cases |
| 💰 **Finance Approver** | `FINANCE_APPROVER` | Financial oversight | Approve cost estimates, budget allocations, financial projections |
| ⚖️ **Legal Approver** | `LEGAL_APPROVER` | Legal compliance | Review legal implications, compliance requirements, risk assessments |
| 🏗️ **Technical Architect** | `TECHNICAL_ARCHITECT` | Senior technical review | Advanced system design approval, architecture decisions |
| 📦 **Product Owner** | `PRODUCT_OWNER` | Product management | PRD approval, feature prioritization, product strategy |
| 📈 **Business Analyst** | `BUSINESS_ANALYST` | Requirements analysis | Edit/review business requirements, process analysis |

## 🔧 Role Assignment

### Using Individual Scripts
```bash
# Assign specific roles using dedicated scripts
python scripts/set_admin_role.py user@company.com
python scripts/set_developer_role.py user@company.com
python scripts/set_sales_manager_role.py user@company.com
python scripts/set_finance_approver_role.py user@company.com
python scripts/set_product_owner_role.py user@company.com
```

### Using Universal Script (Recommended)
```bash
# Universal script for any role
python scripts/set_user_role.py user@company.com ROLE_NAME

# Examples:
python scripts/set_user_role.py john@drfirst.com SALES_MANAGER
python scripts/set_user_role.py jane@drfirst.com FINANCE_APPROVER
python scripts/set_user_role.py tech@drfirst.com TECHNICAL_ARCHITECT
python scripts/set_user_role.py legal@drfirst.com LEGAL_APPROVER
```

### View Available Roles
```bash
python scripts/set_user_role.py
# Displays usage and all available roles
```

## 🔐 Permissions Matrix

### Business Case Lifecycle Permissions

| Action | ADMIN | USER | DEVELOPER | SALES_MANAGER | FINANCE_APPROVER | PRODUCT_OWNER | LEGAL_APPROVER |
|--------|-------|------|-----------|---------------|------------------|---------------|----------------|
| **Create Business Case** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Edit Own PRD** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Approve PRD** | ✅ | ✅* | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Edit System Design** | ✅ | ✅* | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Approve System Design** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Approve Cost Estimates** | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Approve Value Projections** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Final Business Case Approval** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Admin Panel Access** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

*\* Own cases only*

## 🚀 Role Implementation Examples

### Adding New Role-Specific Features

When implementing new features for specific roles, follow this pattern:

#### 1. Backend API Protection
```python
# In your API endpoint
@router.post("/cases/{case_id}/approve-financials")
async def approve_financials(
    case_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    system_role = current_user.get("systemRole")
    
    # Role-based authorization
    if system_role not in ["FINANCE_APPROVER", "ADMIN"]:
        raise HTTPException(
            status_code=403, 
            detail="Only Finance Approvers can approve financial projections."
        )
    
    # ... rest of logic
```

#### 2. Frontend Role-Based UI
```tsx
// In your React component
import { useAuth } from '../contexts/AuthContext';

const BusinessCaseDetailPage = () => {
  const { systemRole } = useAuth();
  
  return (
    <div>
      {/* Show approve button only to Finance Approvers */}
      {systemRole === 'FINANCE_APPROVER' && 
       status === 'FINANCIAL_REVIEW' && (
        <Button onClick={handleApproveFinancials}>
          Approve Financial Projection
        </Button>
      )}
      
      {/* Show different content based on role */}
      {(systemRole === 'SALES_MANAGER' || systemRole === 'ADMIN') && (
        <SalesMetricsPanel />
      )}
    </div>
  );
};
```

## 🔄 Workflow Integration

### Typical Business Case Workflow with Roles

1. **Creation** (Any role) → Business case initiated
2. **PRD Development** (USER/PRODUCT_OWNER) → Requirements documented
3. **PRD Approval** (PRODUCT_OWNER) → Requirements approved
4. **System Design** (DEVELOPER/TECHNICAL_ARCHITECT) → Technical architecture
5. **Design Approval** (DEVELOPER/TECHNICAL_ARCHITECT) → Architecture approved
6. **Cost Estimation** (FINANCE_APPROVER) → Financial analysis
7. **Value Projection** (SALES_MANAGER) → Revenue projections
8. **Legal Review** (LEGAL_APPROVER) → Compliance validation
9. **Final Approval** (ADMIN) → Business case approved

## ⚡ Quick Commands

```bash
# List all roles
python scripts/set_user_role.py

# Assign multiple users to different roles
python scripts/set_user_role.py sales1@drfirst.com SALES_REP
python scripts/set_user_role.py sales2@drfirst.com SALES_MANAGER
python scripts/set_user_role.py finance@drfirst.com FINANCE_APPROVER
python scripts/set_user_role.py legal@drfirst.com LEGAL_APPROVER
python scripts/set_user_role.py architect@drfirst.com TECHNICAL_ARCHITECT
python scripts/set_user_role.py product@drfirst.com PRODUCT_OWNER
python scripts/set_user_role.py analyst@drfirst.com BUSINESS_ANALYST
```

## 🔮 Future Enhancements

### Planned Role Features
- **Role Hierarchies**: ADMIN inherits all permissions
- **Multi-Role Support**: Users can have multiple roles
- **Dynamic Permissions**: Permission-based access control
- **Role Delegation**: Temporary role assignments
- **Audit Trail**: Track role assignments and changes

### Advanced Role Concepts
```python
# Future role hierarchy implementation
ROLE_HIERARCHY = {
    "ADMIN": ["SALES_MANAGER", "FINANCE_APPROVER", "DEVELOPER", "USER"],
    "SALES_MANAGER": ["SALES_REP", "USER"],
    "TECHNICAL_ARCHITECT": ["DEVELOPER", "USER"],
    # etc.
}

# Future permission-based access
class Permission(str, Enum):
    APPROVE_PRD = "approve_prd"
    APPROVE_SYSTEM_DESIGN = "approve_system_design"
    APPROVE_FINANCIALS = "approve_financials"
    APPROVE_LEGAL = "approve_legal"
```

## 📞 Support

For questions about role assignment or permissions:
1. Check this guide first
2. Review the role assignment scripts in `/scripts/`
3. Test with the universal role assignment tool
4. Contact the development team for role hierarchy changes

---

**Status**: ✅ **Production Ready** - All roles implemented and tested
**Last Updated**: January 2025 