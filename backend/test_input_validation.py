#!/usr/bin/env python3
"""
Test script for input validation enhancements.

This script tests the enhanced Pydantic models and API validation
to ensure they properly reject invalid input and accept valid input.
"""

import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Add the backend app to the path
sys.path.append('/app')

from pydantic import ValidationError
from app.models.firestore_models import (
    User, BusinessCaseRequest, BusinessCase, Job, RelevantLink, UserRole, JobStatus
)
from app.api.v1.cases.models import (
    PrdUpdateRequest, StatusUpdateRequest, SystemDesignUpdateRequest,
    EffortEstimateUpdateRequest, CostEstimateUpdateRequest,
    ValueProjectionUpdateRequest, PrdRejectRequest
)
from app.api.v1.agent_routes import BusinessCaseGenerationRequest, AgentActionRequest


def test_user_validation():
    """Test User model validation"""
    print("Testing User model validation...")
    
    # Valid user
    try:
        valid_user = User(
            uid="test_user_123",
            email="test@drfirst.com",
            display_name="Test User",
            systemRole=UserRole.USER
        )
        print("✓ Valid user accepted")
    except ValidationError as e:
        print(f"✗ Valid user rejected: {e}")
    
    # Invalid email domain
    try:
        User(
            uid="test_user_123",
            email="test@gmail.com",
            display_name="Test User"
        )
        print("✗ Invalid email domain accepted")
    except ValidationError:
        print("✓ Invalid email domain rejected")
    
    # Invalid UID format
    try:
        User(
            uid="test user with spaces",
            email="test@drfirst.com"
        )
        print("✗ Invalid UID format accepted")
    except ValidationError:
        print("✓ Invalid UID format rejected")
    
    # Invalid display name
    try:
        User(
            uid="test_user_123",
            email="test@drfirst.com",
            display_name="Test@User#"
        )
        print("✗ Invalid display name accepted")
    except ValidationError:
        print("✓ Invalid display name rejected")


def test_relevant_link_validation():
    """Test RelevantLink model validation"""
    print("\nTesting RelevantLink model validation...")
    
    # Valid link
    try:
        valid_link = RelevantLink(
            name="Google",
            url="https://www.google.com"
        )
        print("✓ Valid link accepted")
    except ValidationError as e:
        print(f"✗ Valid link rejected: {e}")
    
    # Invalid URL
    try:
        RelevantLink(
            name="Invalid Link",
            url="not-a-url"
        )
        print("✗ Invalid URL accepted")
    except ValidationError:
        print("✓ Invalid URL rejected")
    
    # Empty name
    try:
        RelevantLink(
            name="   ",
            url="https://www.google.com"
        )
        print("✗ Empty name accepted")
    except ValidationError:
        print("✓ Empty name rejected")


def test_business_case_request_validation():
    """Test BusinessCaseRequest model validation"""
    print("\nTesting BusinessCaseRequest model validation...")
    
    future_date = datetime.utcnow() + timedelta(days=30)
    
    # Valid request
    try:
        valid_request = BusinessCaseRequest(
            title="Test Business Case",
            description="This is a detailed description of the business case with more than 10 characters.",
            requester_uid="user_123",
            requirements={"description": "Detailed requirements here"},
            priority="high",
            deadline=future_date,
            relevant_links=[
                RelevantLink(name="Reference", url="https://example.com")
            ]
        )
        print("✓ Valid business case request accepted")
    except ValidationError as e:
        print(f"✗ Valid business case request rejected: {e}")
    
    # Title too short
    try:
        BusinessCaseRequest(
            title="AB",
            description="This is a detailed description.",
            requester_uid="user_123"
        )
        print("✗ Short title accepted")
    except ValidationError:
        print("✓ Short title rejected")
    
    # Description too short
    try:
        BusinessCaseRequest(
            title="Valid Title",
            description="Short",
            requester_uid="user_123"
        )
        print("✗ Short description accepted")
    except ValidationError:
        print("✓ Short description rejected")
    
    # Invalid priority
    try:
        BusinessCaseRequest(
            title="Valid Title",
            description="This is a detailed description.",
            requester_uid="user_123",
            priority="invalid_priority"
        )
        print("✗ Invalid priority accepted")
    except ValidationError:
        print("✓ Invalid priority rejected")
    
    # Past deadline
    try:
        past_date = datetime.utcnow() - timedelta(days=1)
        BusinessCaseRequest(
            title="Valid Title",
            description="This is a detailed description.",
            requester_uid="user_123",
            deadline=past_date
        )
        print("✗ Past deadline accepted")
    except ValidationError:
        print("✓ Past deadline rejected")


def test_prd_update_request_validation():
    """Test PrdUpdateRequest model validation"""
    print("\nTesting PrdUpdateRequest model validation...")
    
    # Valid PRD content
    try:
        valid_prd = PrdUpdateRequest(
            content_markdown="# Product Requirements Document\n\nThis is a detailed PRD with substantial content."
        )
        print("✓ Valid PRD content accepted")
    except ValidationError as e:
        print(f"✗ Valid PRD content rejected: {e}")
    
    # Empty content
    try:
        PrdUpdateRequest(content_markdown="")
        print("✗ Empty PRD content accepted")
    except ValidationError:
        print("✓ Empty PRD content rejected")
    
    # Only markdown formatting
    try:
        PrdUpdateRequest(content_markdown="### ## * ** ` ` []")
        print("✗ Only markdown formatting accepted")
    except ValidationError:
        print("✓ Only markdown formatting rejected")


def test_status_update_request_validation():
    """Test StatusUpdateRequest model validation"""
    print("\nTesting StatusUpdateRequest model validation...")
    
    # Valid status
    try:
        valid_status = StatusUpdateRequest(
            status="PRD_REVIEW",
            comment="This is a valid comment"
        )
        print("✓ Valid status update accepted")
    except ValidationError as e:
        print(f"✗ Valid status update rejected: {e}")
    
    # Invalid status format
    try:
        StatusUpdateRequest(status="invalid-status")
        print("✗ Invalid status format accepted")
    except ValidationError:
        print("✓ Invalid status format rejected")
    
    # Comment too short
    try:
        StatusUpdateRequest(
            status="PRD_REVIEW",
            comment="hi"
        )
        print("✗ Short comment accepted")
    except ValidationError:
        print("✓ Short comment rejected")


def test_effort_estimate_validation():
    """Test EffortEstimateUpdateRequest model validation"""
    print("\nTesting EffortEstimateUpdateRequest model validation...")
    
    # Valid effort estimate
    try:
        valid_estimate = EffortEstimateUpdateRequest(
            roles=[
                {"role_name": "Developer", "hours": 100.0},
                {"role_name": "Designer", "hours": 50.0}
            ],
            total_hours=150,
            estimated_duration_weeks=6,
            complexity_assessment="This is a moderate complexity project requiring multiple developers.",
            notes="Additional notes about the estimate"
        )
        print("✓ Valid effort estimate accepted")
    except ValidationError as e:
        print(f"✗ Valid effort estimate rejected: {e}")
    
    # Empty roles list
    try:
        EffortEstimateUpdateRequest(
            roles=[],
            total_hours=100,
            estimated_duration_weeks=4,
            complexity_assessment="Valid assessment"
        )
        print("✗ Empty roles list accepted")
    except ValidationError:
        print("✓ Empty roles list rejected")
    
    # Invalid role structure
    try:
        EffortEstimateUpdateRequest(
            roles=[{"invalid": "structure"}],
            total_hours=100,
            estimated_duration_weeks=4,
            complexity_assessment="Valid assessment"
        )
        print("✗ Invalid role structure accepted")
    except ValidationError:
        print("✓ Invalid role structure rejected")
    
    # Negative hours
    try:
        EffortEstimateUpdateRequest(
            roles=[{"role_name": "Developer", "hours": -10}],
            total_hours=100,
            estimated_duration_weeks=4,
            complexity_assessment="Valid assessment"
        )
        print("✗ Negative hours accepted")
    except ValidationError:
        print("✓ Negative hours rejected")


def test_cost_estimate_validation():
    """Test CostEstimateUpdateRequest model validation"""
    print("\nTesting CostEstimateUpdateRequest model validation...")
    
    # Valid cost estimate
    try:
        valid_cost = CostEstimateUpdateRequest(
            estimated_cost=50000.0,
            currency="USD",
            breakdown_by_role=[
                {"role_name": "Developer", "cost": 30000.0},
                {"role_name": "Designer", "cost": 20000.0}
            ]
        )
        print("✓ Valid cost estimate accepted")
    except ValidationError as e:
        print(f"✗ Valid cost estimate rejected: {e}")
    
    # Invalid currency format
    try:
        CostEstimateUpdateRequest(
            estimated_cost=50000.0,
            currency="Dollar",
            breakdown_by_role=[{"role_name": "Developer", "cost": 50000.0}]
        )
        print("✗ Invalid currency format accepted")
    except ValidationError:
        print("✓ Invalid currency format rejected")
    
    # Negative cost
    try:
        CostEstimateUpdateRequest(
            estimated_cost=-1000.0,
            currency="USD",
            breakdown_by_role=[{"role_name": "Developer", "cost": 50000.0}]
        )
        print("✗ Negative cost accepted")
    except ValidationError:
        print("✓ Negative cost rejected")


def test_agent_request_validation():
    """Test agent request models validation"""
    print("\nTesting agent request models validation...")
    
    # Valid business case generation request
    try:
        valid_gen_request = BusinessCaseGenerationRequest(
            title="Test Business Case",
            requirements={"description": "Detailed requirements here"},
            priority="high"
        )
        print("✓ Valid generation request accepted")
    except ValidationError as e:
        print(f"✗ Valid generation request rejected: {e}")
    
    # Empty requirements
    try:
        BusinessCaseGenerationRequest(
            title="Test Business Case",
            requirements={}
        )
        print("✗ Empty requirements accepted")
    except ValidationError:
        print("✓ Empty requirements rejected")
    
    # Valid agent action request
    try:
        valid_action = AgentActionRequest(
            request_type="echo",
            payload={"input_text": "Hello World"}
        )
        print("✓ Valid agent action accepted")
    except ValidationError as e:
        print(f"✗ Valid agent action rejected: {e}")
    
    # Invalid request type format
    try:
        AgentActionRequest(
            request_type="invalid-type-with-dashes",
            payload={"test": "data"}
        )
        print("✗ Invalid request type format accepted")
    except ValidationError:
        print("✓ Invalid request type format rejected")


def test_job_validation():
    """Test Job model validation"""
    print("\nTesting Job model validation...")
    
    # Valid job
    try:
        valid_job = Job(
            job_type="business_case_generation",
            user_uid="user_123",
            progress=50
        )
        print("✓ Valid job accepted")
    except ValidationError as e:
        print(f"✗ Valid job rejected: {e}")
    
    # Invalid progress range
    try:
        Job(
            job_type="test_job",
            user_uid="user_123",
            progress=150  # Over 100
        )
        print("✗ Invalid progress range accepted")
    except ValidationError:
        print("✓ Invalid progress range rejected")
    
    # Invalid job type format
    try:
        Job(
            job_type="invalid job type",
            user_uid="user_123"
        )
        print("✗ Invalid job type format accepted")
    except ValidationError:
        print("✓ Invalid job type format rejected")


def main():
    """Run all validation tests"""
    print("Starting comprehensive input validation tests...")
    print("=" * 60)
    
    test_user_validation()
    test_relevant_link_validation()
    test_business_case_request_validation()
    test_prd_update_request_validation()
    test_status_update_request_validation()
    test_effort_estimate_validation()
    test_cost_estimate_validation()
    test_agent_request_validation()
    test_job_validation()
    
    print("\n" + "=" * 60)
    print("Input validation tests completed!")
    print("\nNOTE: This tests Pydantic model validation only.")
    print("For full API endpoint testing including FastAPI Query/Path validation,")
    print("run the API server and use the provided test_api_validation.py script.")


if __name__ == "__main__":
    main() 