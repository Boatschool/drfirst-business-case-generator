# Backend Endpoints Needed for Enhanced Agentic Workflow

## Overview
The frontend has been enhanced with manual trigger buttons and auto-progression capabilities, but the corresponding backend endpoints need to be implemented.

## Required Endpoints

### 1. Effort Estimate Generation
```http
POST /api/v1/cases/{caseId}/effort-estimate/generate
```
**Purpose**: Trigger AI agent to generate effort estimates based on approved system design

**Request Body**: None (uses case data from database)

**Response**:
```json
{
  "message": "Effort estimate generation triggered successfully",
  "new_status": "EFFORT_ESTIMATING", 
  "case_id": "string"
}
```

**Workflow**:
1. Validate case exists and system design is approved
2. Trigger PlannerAgent to generate effort estimates
3. Update case status to indicate generation in progress
4. Generate `effort_estimate_v1` data structure
5. Update case status to `PLANNING_COMPLETE`

---

### 2. Cost Analysis Generation
```http
POST /api/v1/cases/{caseId}/cost-analysis/generate
```
**Purpose**: Trigger AI agent to generate cost analysis based on approved effort estimates

**Request Body**: None (uses effort estimate data from database)

**Response**:
```json
{
  "message": "Cost analysis generation triggered successfully",
  "new_status": "COSTING_IN_PROGRESS",
  "case_id": "string"
}
```

**Workflow**:
1. Validate case exists and effort estimate is approved
2. Trigger CostAnalystAgent to generate cost breakdown
3. Apply rate cards and calculate total costs
4. Generate `cost_estimate_v1` data structure
5. Update case status to `COSTING_COMPLETE`

---

### 3. Value Analysis Generation
```http
POST /api/v1/cases/{caseId}/value-analysis/generate
```
**Purpose**: Trigger AI agent to generate value projections based on approved cost estimates

**Request Body**: None (uses cost estimate data from database)

**Response**:
```json
{
  "message": "Value analysis generation triggered successfully",
  "new_status": "VALUE_ANALYSIS_IN_PROGRESS",
  "case_id": "string"
}
```

**Workflow**:
1. Validate case exists and cost estimate is approved
2. Trigger SalesValueAnalystAgent to generate value scenarios
3. Calculate ROI and payback periods
4. Generate `value_projection_v1` data structure
5. Update case status to `VALUE_ANALYSIS_COMPLETE`

---

### 4. Financial Model Generation
```http
POST /api/v1/cases/{caseId}/financial-model/generate
```
**Purpose**: Trigger AI agent to generate comprehensive financial model and recommendations

**Request Body**: None (uses all previous estimates from database)

**Response**:
```json
{
  "message": "Financial model generation triggered successfully",
  "new_status": "FINANCIAL_MODELING_IN_PROGRESS",
  "case_id": "string"
}
```

**Workflow**:
1. Validate case exists and value projection is approved
2. Trigger FinancialModelAgent to compile comprehensive model
3. Generate executive summary and recommendations
4. Generate `financial_summary_v1` data structure
5. Update case status to `FINANCIAL_MODELING_COMPLETE`

---

## Auto-Progression Logic

### Current Approval Methods Need Enhancement:

#### 1. System Design Approval
```python
# In approveSystemDesign endpoint
async def approve_system_design(case_id: str):
    # ... existing approval logic ...
    
    # NEW: Auto-trigger next stage
    try:
        await trigger_effort_estimate_generation(case_id)
        logger.info(f"Auto-triggered effort estimation for case {case_id}")
    except Exception as e:
        logger.warning(f"Auto-progression failed for case {case_id}: {e}")
        # Don't fail the approval if auto-trigger fails
```

#### 2. Effort Estimate Approval
```python
# In approveEffortEstimate endpoint  
async def approve_effort_estimate(case_id: str):
    # ... existing approval logic ...
    
    # NEW: Auto-trigger next stage
    try:
        await trigger_cost_analysis_generation(case_id)
        logger.info(f"Auto-triggered cost analysis for case {case_id}")
    except Exception as e:
        logger.warning(f"Auto-progression failed for case {case_id}: {e}")
```

#### 3. Cost Estimate Approval
```python
# In approveCostEstimate endpoint
async def approve_cost_estimate(case_id: str):
    # ... existing approval logic ...
    
    # NEW: Auto-trigger next stage
    try:
        await trigger_value_analysis_generation(case_id)
        logger.info(f"Auto-triggered value analysis for case {case_id}")
    except Exception as e:
        logger.warning(f"Auto-progression failed for case {case_id}: {e}")
```

#### 4. Value Projection Approval
```python
# In approveValueProjection endpoint
async def approve_value_projection(case_id: str):
    # ... existing approval logic ...
    
    # NEW: Auto-trigger next stage
    try:
        await trigger_financial_model_generation(case_id)
        logger.info(f"Auto-triggered financial model for case {case_id}")
    except Exception as e:
        logger.warning(f"Auto-progression failed for case {case_id}: {e}")
```

---

## Error Handling

### Standard Error Responses:
```json
{
  "error": {
    "message": "Error description",
    "error_code": "GENERATION_FAILED",
    "details": {
      "case_id": "string",
      "stage": "effort_estimation",
      "reason": "System design not approved"
    }
  }
}
```

### Common Error Cases:
- **404**: Case not found
- **400**: Prerequisites not met (e.g., previous stage not approved)
- **409**: Generation already in progress
- **500**: AI agent failure

---

## Status Flow

```
SYSTEM_DESIGN_APPROVED 
  → [trigger] → EFFORT_ESTIMATING 
  → PLANNING_COMPLETE 
  → [approve] → EFFORT_APPROVED
  → [trigger] → COSTING_IN_PROGRESS
  → COSTING_COMPLETE
  → [approve] → COSTING_APPROVED  
  → [trigger] → VALUE_ANALYSIS_IN_PROGRESS
  → VALUE_ANALYSIS_COMPLETE
  → [approve] → VALUE_APPROVED
  → [trigger] → FINANCIAL_MODELING_IN_PROGRESS
  → FINANCIAL_MODELING_COMPLETE
  → [approve] → CASE_READY_FOR_FINAL_APPROVAL
```

---

## Implementation Priority

1. **High Priority**: Effort Estimate Generation (most commonly needed)
2. **Medium Priority**: Cost Analysis Generation
3. **Medium Priority**: Value Analysis Generation  
4. **Low Priority**: Financial Model Generation (can use existing FinancialEstimatesSection)

---

## Testing

### Manual Testing:
1. Approve System Design → Should auto-trigger Effort Estimation
2. Click "Generate Effort Estimate" button → Should call endpoint and generate data
3. Approve Effort Estimate → Should auto-trigger Cost Analysis
4. Continue through full workflow

### Expected Frontend Behavior:
- ✅ Better error messages (implemented)
- ✅ Loading states during generation
- ✅ Success messages when generation completes
- ✅ Auto-refresh case details after generation
- ✅ Manual fallback buttons if auto-progression fails 