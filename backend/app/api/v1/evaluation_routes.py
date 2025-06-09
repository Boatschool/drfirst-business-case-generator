"""
Evaluation API routes for the DrFirst Business Case Generator
Handles human evaluation submissions and storage
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from google.cloud import firestore
from app.auth.firebase_auth import require_admin_role
from app.core.config import settings
from pydantic import BaseModel, Field
import json
import os

# Import dashboard routes
from . import dashboard_routes

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Include dashboard routes under /dashboard prefix
router.include_router(
    dashboard_routes.router,
    prefix="/dashboard",
    tags=["Automated Evaluation Dashboard"]
)


# Pydantic models for evaluation submission
class MetricScoreComment(BaseModel):
    """Individual metric score and comment"""
    score: int = Field(..., ge=1, le=5, description="Score from 1 to 5")
    comment: str = Field("", description="Evaluator comments for this metric")


class HumanEvaluationSubmission(BaseModel):
    """Request model for human evaluation submission"""
    eval_id: str = Field(..., description="Unique evaluation ID")
    golden_dataset_inputId: str = Field(..., description="Golden dataset input ID")
    case_id: Optional[str] = Field(None, description="Case ID if available")
    trace_id: Optional[str] = Field(None, description="Trace ID if available")
    agent_name: str = Field(..., description="Name of the agent being evaluated")
    
    # Dynamic metric scores and comments - will be validated based on agent
    metric_scores_and_comments: Dict[str, MetricScoreComment] = Field(
        ..., description="Dictionary of metric names to scores and comments"
    )
    
    # Overall assessment
    overall_quality_score: int = Field(..., ge=1, le=5, description="Overall quality score from 1 to 5")
    overall_comments: str = Field("", description="Overall evaluator comments")


class EvaluationResponse(BaseModel):
    """Response model for successful evaluation submission"""
    success: bool
    submission_id: str
    message: str


class EvaluationTask(BaseModel):
    """Model for evaluation task display"""
    eval_id: str
    golden_dataset_inputId: str
    case_id: Optional[str]
    trace_id: Optional[str]
    agent_name: str
    input_payload_summary: str
    agent_output_to_evaluate: str
    expected_characteristics: Optional[Dict[str, Any]]
    applicable_metrics: List[str]


# Agent metric definitions based on evaluation_metrics_definition.md
AGENT_HUMAN_METRICS = {
    "ProductManagerAgent": [
        "Content_Relevance_Quality"
    ],
    "ArchitectAgent": [
        "Plausibility_Appropriateness",
        "Clarity_Understandability"
    ],
    "PlannerAgent": [
        "Reasonableness_Hours",
        "Quality_Rationale"
    ],
    "SalesValueAnalystAgent": [
        "Plausibility_Projections"
    ],
    "CostAnalystAgent": [],  # No human metrics defined
    "FinancialModelAgent": []  # No human metrics defined
}


# Lazy initialization of Firestore client
_db_instance = None
_db_initialized = False


def get_evaluation_db():
    """Get Firestore client with lazy initialization"""
    global _db_instance, _db_initialized
    if not _db_initialized:
        try:
            _db_instance = firestore.Client(project=settings.firebase_project_id)
            _db_initialized = True
            logger.info("Evaluation routes: Firestore client initialized successfully.")
        except Exception as e:
            logger.error(f"Evaluation routes: Failed to initialize Firestore client: {e}")
            _db_instance = None
    return _db_instance


def validate_metric_scores(agent_name: str, metric_scores: Dict[str, MetricScoreComment]) -> None:
    """Validate that the submitted metrics are appropriate for the agent"""
    expected_metrics = AGENT_HUMAN_METRICS.get(agent_name, [])
    
    # Check if all expected metrics are present
    for expected_metric in expected_metrics:
        if expected_metric not in metric_scores:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required metric '{expected_metric}' for agent '{agent_name}'"
            )
    
    # Check for unexpected metrics
    for submitted_metric in metric_scores.keys():
        if submitted_metric not in expected_metrics:
            raise HTTPException(
                status_code=400,
                detail=f"Unexpected metric '{submitted_metric}' for agent '{agent_name}'. Expected: {expected_metrics}"
            )


@router.get("/tasks", response_model=List[EvaluationTask], summary="Get available evaluation tasks")
async def get_evaluation_tasks(
    current_user: dict = Depends(require_admin_role)
):
    """
    Get list of available evaluation tasks from the evaluation batch file
    """
    try:
        # Load the evaluation batch file
        batch_file_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "..", "evaluations", 
            "human_eval_batch_01_inputs_outputs.json"
        )
        
        if not os.path.exists(batch_file_path):
            raise HTTPException(
                status_code=404,
                detail="Evaluation batch file not found"
            )
        
        with open(batch_file_path, 'r') as f:
            batch_data = json.load(f)
        
        tasks = []
        for entry in batch_data.get("evaluation_entries", []):
            # Get applicable metrics for this agent
            agent_name = entry.get("agent_name", "")
            applicable_metrics = AGENT_HUMAN_METRICS.get(agent_name, [])
            
            task = EvaluationTask(
                eval_id=entry.get("eval_id", ""),
                golden_dataset_inputId=entry.get("golden_dataset_inputId", ""),
                case_id=entry.get("case_id"),
                trace_id=entry.get("trace_id"),
                agent_name=agent_name,
                input_payload_summary=entry.get("input_payload_summary", ""),
                agent_output_to_evaluate=entry.get("agent_output_to_evaluate", ""),
                expected_characteristics=entry.get("expected_characteristics"),
                applicable_metrics=applicable_metrics
            )
            tasks.append(task)
        
        logger.info(f"Loaded {len(tasks)} evaluation tasks for user {current_user.get('uid')}")
        return tasks
        
    except Exception as e:
        logger.error(f"Error loading evaluation tasks: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to load evaluation tasks"
        )


@router.post("/submit", response_model=EvaluationResponse, summary="Submit human evaluation")
async def submit_evaluation(
    evaluation: HumanEvaluationSubmission,
    current_user: dict = Depends(require_admin_role)
):
    """
    Submit a human evaluation result to Firestore
    """
    try:
        # Validate metrics for the agent
        validate_metric_scores(evaluation.agent_name, evaluation.metric_scores_and_comments)
        
        # Get Firestore client
        db = get_evaluation_db()
        if not db:
            raise HTTPException(
                status_code=500,
                detail="Database connection not available"
            )
        
        # Prepare evaluation document
        submission_id = f"eval_submission_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.get('uid', 'unknown')[:8]}"
        
        # Convert MetricScoreComment objects to dictionaries
        metric_scores_dict = {}
        for metric_name, score_comment in evaluation.metric_scores_and_comments.items():
            metric_scores_dict[metric_name] = {
                "score": score_comment.score,
                "comment": score_comment.comment
            }
        
        evaluation_doc = {
            "submission_id": submission_id,
            "eval_id": evaluation.eval_id,
            "golden_dataset_inputId": evaluation.golden_dataset_inputId,
            "case_id": evaluation.case_id,
            "trace_id": evaluation.trace_id,
            "agent_name": evaluation.agent_name,
            "evaluator_id": current_user.get("uid"),
            "evaluator_email": current_user.get("email"),
            "evaluation_date": datetime.now(timezone.utc),
            "metric_scores_and_comments": metric_scores_dict,
            "overall_quality_score": evaluation.overall_quality_score,
            "overall_comments": evaluation.overall_comments,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Save to Firestore
        collection_ref = db.collection("humanEvaluationResults")
        doc_ref = collection_ref.document(submission_id)
        doc_ref.set(evaluation_doc)
        
        logger.info(f"Human evaluation submitted successfully: {submission_id} by {current_user.get('email')}")
        
        return EvaluationResponse(
            success=True,
            submission_id=submission_id,
            message="Evaluation submitted successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Error submitting evaluation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to submit evaluation"
        )


@router.get("/results", response_model=List[Dict[str, Any]], summary="Get evaluation results")
async def get_evaluation_results(
    current_user: dict = Depends(require_admin_role),
    agent_name: Optional[str] = None,
    evaluator_id: Optional[str] = None,
    limit: int = 50
):
    """
    Get submitted evaluation results with optional filtering
    """
    try:
        db = get_evaluation_db()
        if not db:
            raise HTTPException(
                status_code=500,
                detail="Database connection not available"
            )
        
        # Build query
        query = db.collection("humanEvaluationResults")
        
        if agent_name:
            query = query.where("agent_name", "==", agent_name)
        
        if evaluator_id:
            query = query.where("evaluator_id", "==", evaluator_id)
        
        # Order by evaluation date (most recent first) and limit results
        query = query.order_by("evaluation_date", direction=firestore.Query.DESCENDING).limit(limit)
        
        results = []
        for doc in query.stream():
            doc_data = doc.to_dict()
            # Convert Firestore timestamps to ISO strings
            if "evaluation_date" in doc_data and doc_data["evaluation_date"]:
                doc_data["evaluation_date"] = doc_data["evaluation_date"].isoformat()
            if "created_at" in doc_data and doc_data["created_at"]:
                doc_data["created_at"] = doc_data["created_at"].isoformat()
            if "updated_at" in doc_data and doc_data["updated_at"]:
                doc_data["updated_at"] = doc_data["updated_at"].isoformat()
            results.append(doc_data)
        
        logger.info(f"Retrieved {len(results)} evaluation results")
        return results
        
    except Exception as e:
        logger.error(f"Error retrieving evaluation results: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve evaluation results"
        )


@router.get("/metrics/{agent_name}", response_model=List[str], summary="Get metrics for agent")
async def get_agent_metrics(
    agent_name: str,
    current_user: dict = Depends(require_admin_role)
):
    """
    Get list of human evaluation metrics for a specific agent
    """
    metrics = AGENT_HUMAN_METRICS.get(agent_name, [])
    return metrics 