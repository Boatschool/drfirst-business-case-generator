"""
Dashboard API routes for automated evaluation results
Handles dashboard data retrieval and visualization for evaluation monitoring
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from google.cloud import firestore
from app.auth.firebase_auth import require_admin_role
from app.core.config import settings
from pydantic import BaseModel, Field
import math
import asyncio
import subprocess
import os
import uuid
import json

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Firestore collection names (matching those from run_automated_evals.py)
AUTOMATED_EVAL_RESULTS_COLLECTION = "automatedEvaluationResults"
AUTOMATED_EVAL_RUNS_COLLECTION = "automatedEvaluationRuns"
HUMAN_EVAL_RESULTS_COLLECTION = "humanEvaluationResults"

# Lazy initialization of Firestore client
_db_instance = None
_db_initialized = False


def get_dashboard_db():
    """Get Firestore client with lazy initialization"""
    global _db_instance, _db_initialized
    if not _db_initialized:
        try:
            _db_instance = firestore.Client(project=settings.firebase_project_id)
            _db_initialized = True
            logger.info("Dashboard routes: Firestore client initialized successfully.")
        except Exception as e:
            logger.error(f"Dashboard routes: Failed to initialize Firestore client: {e}")
            _db_instance = None
    return _db_instance


# Pydantic models for request/response
class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints"""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    limit: int = Field(10, ge=1, le=100, description="Items per page")
    sort_by: str = Field("run_timestamp_start", description="Field to sort by")
    order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")


class DashboardSummaryData(BaseModel):
    """Summary statistics for the dashboard"""
    total_runs: int
    total_examples_processed: int
    latest_run_success_rate: Optional[float]
    latest_run_validation_pass_rate: Optional[float]
    latest_run_timestamp: Optional[str]
    overall_avg_success_rate: float
    overall_avg_validation_pass_rate: float


class EvaluationRunSummary(BaseModel):
    """Summary of a single evaluation run"""
    eval_run_id: str
    run_timestamp_start: str
    run_timestamp_end: str
    total_examples_processed: int
    successful_agent_runs: int
    failed_agent_runs: int
    overall_validation_passed_count: int
    dataset_file_used: str
    success_rate_percentage: float
    validation_pass_rate_percentage: float
    total_evaluation_time_seconds: int


class PaginatedRunListData(BaseModel):
    """Paginated list of evaluation runs"""
    runs: List[EvaluationRunSummary]
    total_count: int
    current_page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class FailedValidationEntry(BaseModel):
    """Details of a failed validation entry"""
    golden_dataset_inputId: str
    agent_name: str
    agent_run_status: str
    validation_results: Dict[str, Any]
    agent_error_message: Optional[str]
    execution_time_ms: int
    processed_at: str


class RunDetailsData(BaseModel):
    """Detailed view of a specific evaluation run"""
    run_summary: EvaluationRunSummary
    agent_specific_statistics: Dict[str, Any]
    failed_validations: List[FailedValidationEntry]
    failed_validations_count: int


# Human Evaluation Models
class HumanEvalSummaryData(BaseModel):
    """Summary statistics for human evaluations"""
    total_evaluations: int
    unique_evaluators: int
    average_overall_score: float
    score_distribution: Dict[str, int]  # {"1": count, "2": count, ...}
    evaluations_by_agent: Dict[str, int]
    latest_evaluation_date: Optional[str]


class HumanEvaluationResult(BaseModel):
    """Individual human evaluation result"""
    submission_id: str
    eval_id: str
    golden_dataset_inputId: str
    case_id: Optional[str]
    trace_id: Optional[str]
    agent_name: str
    evaluator_id: str
    evaluator_email: str
    evaluation_date: str
    overall_quality_score: int
    overall_comments: str
    metric_scores_and_comments: Dict[str, Any]
    created_at: str
    updated_at: str


class PaginatedHumanEvalData(BaseModel):
    """Paginated list of human evaluation results"""
    evaluations: List[HumanEvaluationResult]
    total_count: int
    current_page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class HumanEvalResultDetail(BaseModel):
    """Detailed view of a specific human evaluation"""
    submission_id: str
    eval_id: str
    golden_dataset_inputId: str
    case_id: Optional[str]
    trace_id: Optional[str]
    agent_name: str
    evaluator_id: str
    evaluator_email: str
    evaluation_date: str
    overall_quality_score: int
    overall_comments: str
    metric_scores_and_comments: Dict[str, Any]
    created_at: str
    updated_at: str


class HumanEvalFilters(BaseModel):
    """Filters for human evaluation results"""
    agent_name: Optional[str] = None
    evaluator_id: Optional[str] = None
    golden_dataset_inputId: Optional[str] = None


def convert_firestore_timestamp(value) -> Optional[str]:
    """Convert Firestore timestamp to ISO string"""
    if value is None:
        return None
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value)


@router.get("/summary", response_model=DashboardSummaryData, summary="Get dashboard summary metrics")
async def get_dashboard_summary(
    current_user: dict = Depends(require_admin_role)
):
    """
    Get overall summary metrics for the automated evaluation dashboard
    """
    try:
        db = get_dashboard_db()
        if not db:
            raise HTTPException(
                status_code=500,
                detail="Database connection not available"
            )
        
        # Query all evaluation runs
        runs_collection = db.collection(AUTOMATED_EVAL_RUNS_COLLECTION)
        runs_query = runs_collection.order_by("run_timestamp_start", direction=firestore.Query.DESCENDING)
        runs_docs = list(runs_query.stream())
        
        if not runs_docs:
            # No runs found - return zeros
            return DashboardSummaryData(
                total_runs=0,
                total_examples_processed=0,
                latest_run_success_rate=None,
                latest_run_validation_pass_rate=None,
                latest_run_timestamp=None,
                overall_avg_success_rate=0.0,
                overall_avg_validation_pass_rate=0.0
            )
        
        # Calculate summary statistics
        total_runs = len(runs_docs)
        total_examples = 0
        success_rates = []
        validation_rates = []
        
        latest_run_data = runs_docs[0].to_dict()  # Most recent run
        
        for doc in runs_docs:
            data = doc.to_dict()
            total_examples += data.get("total_examples_processed", 0)
            
            success_rate = data.get("success_rate_percentage", 0.0)
            validation_rate = data.get("validation_pass_rate_percentage", 0.0)
            
            success_rates.append(success_rate)
            validation_rates.append(validation_rate)
        
        # Calculate averages
        overall_avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0
        overall_avg_validation_pass_rate = sum(validation_rates) / len(validation_rates) if validation_rates else 0.0
        
        return DashboardSummaryData(
            total_runs=total_runs,
            total_examples_processed=total_examples,
            latest_run_success_rate=latest_run_data.get("success_rate_percentage"),
            latest_run_validation_pass_rate=latest_run_data.get("validation_pass_rate_percentage"),
            latest_run_timestamp=convert_firestore_timestamp(latest_run_data.get("run_timestamp_end")),
            overall_avg_success_rate=round(overall_avg_success_rate, 2),
            overall_avg_validation_pass_rate=round(overall_avg_validation_pass_rate, 2)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving dashboard summary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve dashboard summary"
        )


@router.get("/runs", response_model=PaginatedRunListData, summary="Get paginated list of evaluation runs")
async def list_evaluation_runs(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("run_timestamp_start", description="Field to sort by"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: dict = Depends(require_admin_role)
):
    """
    Get paginated and sortable list of evaluation runs
    """
    try:
        db = get_dashboard_db()
        if not db:
            raise HTTPException(
                status_code=500,
                detail="Database connection not available"
            )
        
        # Build query
        runs_collection = db.collection(AUTOMATED_EVAL_RUNS_COLLECTION)
        
        # Handle sorting
        sort_direction = firestore.Query.DESCENDING if order == "desc" else firestore.Query.ASCENDING
        
        # Valid sort fields
        valid_sort_fields = [
            "run_timestamp_start", "run_timestamp_end", "total_examples_processed",
            "success_rate_percentage", "validation_pass_rate_percentage", 
            "total_evaluation_time_seconds"
        ]
        
        if sort_by not in valid_sort_fields:
            sort_by = "run_timestamp_start"
        
        # Get total count for pagination
        total_count = len(list(runs_collection.stream()))
        
        # Calculate pagination
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 1
        offset = (page - 1) * limit
        
        # Get paginated results
        query = runs_collection.order_by(sort_by, direction=sort_direction)
        
        # Apply pagination by getting all docs and slicing (not ideal for large datasets)
        all_docs = list(query.stream())
        paginated_docs = all_docs[offset:offset + limit]
        
        # Convert to response format
        runs = []
        for doc in paginated_docs:
            data = doc.to_dict()
            run_summary = EvaluationRunSummary(
                eval_run_id=data.get("eval_run_id", doc.id),
                run_timestamp_start=convert_firestore_timestamp(data.get("run_timestamp_start")) or "",
                run_timestamp_end=convert_firestore_timestamp(data.get("run_timestamp_end")) or "",
                total_examples_processed=data.get("total_examples_processed", 0),
                successful_agent_runs=data.get("successful_agent_runs", 0),
                failed_agent_runs=data.get("failed_agent_runs", 0),
                overall_validation_passed_count=data.get("overall_validation_passed_count", 0),
                dataset_file_used=data.get("dataset_file_used", ""),
                success_rate_percentage=data.get("success_rate_percentage", 0.0),
                validation_pass_rate_percentage=data.get("validation_pass_rate_percentage", 0.0),
                total_evaluation_time_seconds=data.get("total_evaluation_time_seconds", 0)
            )
            runs.append(run_summary)
        
        return PaginatedRunListData(
            runs=runs,
            total_count=total_count,
            current_page=page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error retrieving evaluation runs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve evaluation runs"
        )


@router.get("/runs/{eval_run_id}/details", response_model=RunDetailsData, summary="Get detailed view of evaluation run")
async def get_evaluation_run_details(
    eval_run_id: str,
    current_user: dict = Depends(require_admin_role)
):
    """
    Get detailed information about a specific evaluation run including failed validations
    """
    try:
        db = get_dashboard_db()
        if not db:
            raise HTTPException(
                status_code=500,
                detail="Database connection not available"
            )
        
        # Get run summary
        run_doc_ref = db.collection(AUTOMATED_EVAL_RUNS_COLLECTION).document(eval_run_id)
        run_doc = run_doc_ref.get()
        
        if not run_doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Evaluation run {eval_run_id} not found"
            )
        
        run_data = run_doc.to_dict()
        
        # Convert to EvaluationRunSummary
        run_summary = EvaluationRunSummary(
            eval_run_id=eval_run_id,
            run_timestamp_start=convert_firestore_timestamp(run_data.get("run_timestamp_start")) or "",
            run_timestamp_end=convert_firestore_timestamp(run_data.get("run_timestamp_end")) or "",
            total_examples_processed=run_data.get("total_examples_processed", 0),
            successful_agent_runs=run_data.get("successful_agent_runs", 0),
            failed_agent_runs=run_data.get("failed_agent_runs", 0),
            overall_validation_passed_count=run_data.get("overall_validation_passed_count", 0),
            dataset_file_used=run_data.get("dataset_file_used", ""),
            success_rate_percentage=run_data.get("success_rate_percentage", 0.0),
            validation_pass_rate_percentage=run_data.get("validation_pass_rate_percentage", 0.0),
            total_evaluation_time_seconds=run_data.get("total_evaluation_time_seconds", 0)
        )
        
        # Get failed validation entries
        results_collection = db.collection(AUTOMATED_EVAL_RESULTS_COLLECTION)
        failed_query = results_collection.where("eval_run_id", "==", eval_run_id).where("overall_automated_eval_passed", "==", False)
        
        failed_validations = []
        for doc in failed_query.stream():
            data = doc.to_dict()
            failed_entry = FailedValidationEntry(
                golden_dataset_inputId=data.get("golden_dataset_inputId", ""),
                agent_name=data.get("agent_name", ""),
                agent_run_status=data.get("agent_run_status", ""),
                validation_results=data.get("validation_results", {}),
                agent_error_message=data.get("agent_error_message", ""),
                execution_time_ms=data.get("execution_time_ms", 0),
                processed_at=data.get("processed_at", "")
            )
            failed_validations.append(failed_entry)
        
        # Get agent-specific statistics
        agent_specific_statistics = run_data.get("agent_specific_statistics", {})
        
        return RunDetailsData(
            run_summary=run_summary,
            agent_specific_statistics=agent_specific_statistics,
            failed_validations=failed_validations,
            failed_validations_count=len(failed_validations)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving evaluation run details for {eval_run_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve evaluation run details"
        )


# Human Evaluation Endpoints


@router.get("/human/summary", response_model=HumanEvalSummaryData, summary="Get human evaluation summary")
async def get_human_eval_summary(
    current_user: dict = Depends(require_admin_role)
):
    """
    Get summary statistics for human evaluations
    """
    try:
        db = get_dashboard_db()
        if not db:
            raise HTTPException(
                status_code=500,
                detail="Database connection not available"
            )
        
        # Query all human evaluation results
        human_results_ref = db.collection(HUMAN_EVAL_RESULTS_COLLECTION)
        docs = list(human_results_ref.stream())
        
        if not docs:
            return HumanEvalSummaryData(
                total_evaluations=0,
                unique_evaluators=0,
                average_overall_score=0.0,
                score_distribution={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                evaluations_by_agent={},
                latest_evaluation_date=None
            )
        
        # Process documents
        evaluator_ids = set()
        overall_scores = []
        score_distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        evaluations_by_agent = {}
        latest_eval_date = None
        
        for doc in docs:
            data = doc.to_dict()
            
            # Collect evaluator IDs
            if data.get("evaluator_id"):
                evaluator_ids.add(data["evaluator_id"])
            
            # Collect overall scores
            overall_score = data.get("overall_quality_score")
            if overall_score:
                overall_scores.append(overall_score)
                score_distribution[str(overall_score)] += 1
            
            # Count evaluations by agent
            agent_name = data.get("agent_name")
            if agent_name:
                evaluations_by_agent[agent_name] = evaluations_by_agent.get(agent_name, 0) + 1
            
            # Track latest evaluation date
            eval_date = data.get("evaluation_date")
            if eval_date:
                # Convert to string if it's a Firestore timestamp
                if hasattr(eval_date, 'isoformat'):
                    eval_date_str = eval_date.isoformat()
                else:
                    eval_date_str = str(eval_date)
                
                if latest_eval_date is None or eval_date_str > latest_eval_date:
                    latest_eval_date = eval_date_str
        
        # Calculate average score
        avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
        
        return HumanEvalSummaryData(
            total_evaluations=len(docs),
            unique_evaluators=len(evaluator_ids),
            average_overall_score=round(avg_score, 2),
            score_distribution=score_distribution,
            evaluations_by_agent=evaluations_by_agent,
            latest_evaluation_date=latest_eval_date
        )
        
    except Exception as e:
        logger.error(f"Error retrieving human evaluation summary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve human evaluation summary"
        )


@router.get("/human/results", response_model=PaginatedHumanEvalData, summary="Get human evaluation results")
async def get_human_eval_results(
    page: int = 1,
    limit: int = 20,
    sort_by: str = "evaluation_date",
    order: str = "desc",
    agent_name: Optional[str] = None,
    evaluator_id: Optional[str] = None,
    golden_dataset_inputId: Optional[str] = None,
    current_user: dict = Depends(require_admin_role)
):
    """
    Get paginated and filterable list of human evaluation results
    """
    try:
        db = get_dashboard_db()
        if not db:
            raise HTTPException(
                status_code=500,
                detail="Database connection not available"
            )
        
        # Build query
        query = db.collection(HUMAN_EVAL_RESULTS_COLLECTION)
        
        # Apply filters
        if agent_name:
            query = query.where("agent_name", "==", agent_name)
        if evaluator_id:
            query = query.where("evaluator_id", "==", evaluator_id)
        if golden_dataset_inputId:
            query = query.where("golden_dataset_inputId", "==", golden_dataset_inputId)
        
        # Get total count for pagination
        total_docs = list(query.stream())
        total_count = len(total_docs)
        
        # Apply sorting and pagination
        if sort_by in ["evaluation_date", "created_at", "updated_at", "overall_quality_score"]:
            if sort_by in ["evaluation_date", "created_at", "updated_at"]:
                direction = firestore.Query.DESCENDING if order == "desc" else firestore.Query.ASCENDING
            else:  # overall_quality_score
                direction = firestore.Query.DESCENDING if order == "desc" else firestore.Query.ASCENDING
            
            query = query.order_by(sort_by, direction=direction)
        
        # Calculate pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        # Execute query
        docs = list(query.stream())
        
        # Convert results
        evaluations = []
        for doc in docs:
            data = doc.to_dict()
            
            # Convert timestamps to strings
            evaluation_date = convert_firestore_timestamp(data.get("evaluation_date"))
            created_at = convert_firestore_timestamp(data.get("created_at"))
            updated_at = convert_firestore_timestamp(data.get("updated_at"))
            
            evaluations.append(HumanEvaluationResult(
                submission_id=data.get("submission_id", ""),
                eval_id=data.get("eval_id", ""),
                golden_dataset_inputId=data.get("golden_dataset_inputId", ""),
                case_id=data.get("case_id"),
                trace_id=data.get("trace_id"),
                agent_name=data.get("agent_name", ""),
                evaluator_id=data.get("evaluator_id", ""),
                evaluator_email=data.get("evaluator_email", ""),
                evaluation_date=evaluation_date or "",
                overall_quality_score=data.get("overall_quality_score", 0),
                overall_comments=data.get("overall_comments", ""),
                metric_scores_and_comments=data.get("metric_scores_and_comments", {}),
                created_at=created_at or "",
                updated_at=updated_at or ""
            ))
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_previous = page > 1
        
        return PaginatedHumanEvalData(
            evaluations=evaluations,
            total_count=total_count,
            current_page=page,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
        
    except Exception as e:
        logger.error(f"Error retrieving human evaluation results: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve human evaluation results"
        )


@router.get("/human/results/{submission_id}", response_model=HumanEvalResultDetail, summary="Get human evaluation detail")
async def get_human_eval_detail(
    submission_id: str,
    current_user: dict = Depends(require_admin_role)
):
    """
    Get detailed view of a specific human evaluation
    """
    try:
        db = get_dashboard_db()
        if not db:
            raise HTTPException(
                status_code=500,
                detail="Database connection not available"
            )
        
        # Get specific document
        doc_ref = db.collection(HUMAN_EVAL_RESULTS_COLLECTION).document(submission_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Human evaluation not found: {submission_id}"
            )
        
        data = doc.to_dict()
        
        # Convert timestamps to strings
        evaluation_date = convert_firestore_timestamp(data.get("evaluation_date"))
        created_at = convert_firestore_timestamp(data.get("created_at"))
        updated_at = convert_firestore_timestamp(data.get("updated_at"))
        
        return HumanEvalResultDetail(
            submission_id=data.get("submission_id", ""),
            eval_id=data.get("eval_id", ""),
            golden_dataset_inputId=data.get("golden_dataset_inputId", ""),
            case_id=data.get("case_id"),
            trace_id=data.get("trace_id"),
            agent_name=data.get("agent_name", ""),
            evaluator_id=data.get("evaluator_id", ""),
            evaluator_email=data.get("evaluator_email", ""),
            evaluation_date=evaluation_date or "",
            overall_quality_score=data.get("overall_quality_score", 0),
            overall_comments=data.get("overall_comments", ""),
            metric_scores_and_comments=data.get("metric_scores_and_comments", {}),
            created_at=created_at or "",
            updated_at=updated_at or ""
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving human evaluation detail: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve human evaluation detail"
        ) 


# Evaluation Job Management
evaluation_jobs = {}  # Simple in-memory job tracking


class EvaluationTriggerResponse(BaseModel):
    """Response from triggering an evaluation"""
    job_id: str
    message: str
    status: str


class EvaluationStatusResponse(BaseModel):
    """Response with evaluation job status"""
    job_id: str
    status: str
    completed: bool
    success: Optional[bool]
    start_time: Optional[str]
    end_time: Optional[str]
    error_message: Optional[str]
    eval_run_id: Optional[str]


@router.post("/evaluations/runs/trigger", response_model=EvaluationTriggerResponse, summary="Trigger new automated evaluation")
async def trigger_evaluation(
    current_user: dict = Depends(require_admin_role)
):
    """
    Trigger a new automated evaluation run
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Store job status
        evaluation_jobs[job_id] = {
            "status": "starting",
            "completed": False,
            "success": None,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "error_message": None,
            "eval_run_id": None
        }
        
        # Start evaluation in background
        asyncio.create_task(run_evaluation_background(job_id))
        
        return EvaluationTriggerResponse(
            job_id=job_id,
            message="Evaluation started successfully",
            status="starting"
        )
        
    except Exception as e:
        logger.error(f"Error triggering evaluation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to trigger evaluation"
        )


@router.get("/evaluations/runs/status/{job_id}", response_model=EvaluationStatusResponse, summary="Get evaluation job status")
async def get_evaluation_status(
    job_id: str,
    current_user: dict = Depends(require_admin_role)
):
    """
    Get status of an evaluation job
    """
    if job_id not in evaluation_jobs:
        raise HTTPException(
            status_code=404,
            detail="Evaluation job not found"
        )
    
    job_info = evaluation_jobs[job_id]
    
    return EvaluationStatusResponse(
        job_id=job_id,
        status=job_info["status"],
        completed=job_info["completed"],
        success=job_info["success"],
        start_time=job_info["start_time"],
        end_time=job_info["end_time"],
        error_message=job_info["error_message"],
        eval_run_id=job_info["eval_run_id"]
    )


async def run_evaluation_background(job_id: str):
    """
    Run the evaluation script in the background
    """
    try:
        # Update job status
        evaluation_jobs[job_id]["status"] = "running"
        
        # Get the backend directory path
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        evaluations_dir = os.path.join(backend_dir, "evaluations")
        eval_script = os.path.join(evaluations_dir, "run_automated_evals.py")
        golden_dataset = os.path.join(evaluations_dir, "golden_datasets_v1.json")
        
        # Build command
        cmd = [
            "python",
            eval_script,
            "--dataset-path", golden_dataset,
            "--output-format", "both"
        ]
        
        # Run the evaluation
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=backend_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # Parse the output to get eval_run_id
            output_text = stdout.decode()
            eval_run_id = None
            
            # Look for eval_run_id in the output
            for line in output_text.split('\n'):
                if 'eval_run_id' in line.lower() or 'evaluation run id' in line.lower():
                    # Try to extract UUID pattern
                    import re
                    uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
                    match = re.search(uuid_pattern, line)
                    if match:
                        eval_run_id = match.group()
                        break
            
            evaluation_jobs[job_id].update({
                "status": "completed",
                "completed": True,
                "success": True,
                "end_time": datetime.now().isoformat(),
                "eval_run_id": eval_run_id
            })
            
            logger.info(f"Evaluation {job_id} completed successfully. Eval run ID: {eval_run_id}")
            
        else:
            error_text = stderr.decode() if stderr else "Unknown error"
            evaluation_jobs[job_id].update({
                "status": "failed",
                "completed": True,
                "success": False,
                "end_time": datetime.now().isoformat(),
                "error_message": error_text
            })
            
            logger.error(f"Evaluation {job_id} failed: {error_text}")
            
    except Exception as e:
        evaluation_jobs[job_id].update({
            "status": "error",
            "completed": True,
            "success": False,
            "end_time": datetime.now().isoformat(),
            "error_message": str(e)
        })
        
        logger.error(f"Error running evaluation {job_id}: {e}")