#!/usr/bin/env python3
"""
DrFirst Business Case Generator - End-to-End Workflow Test Script

This script tests the complete "happy path" business case workflow from initiation
through final approval, simulating different user roles for each approval stage.

Features:
- Firebase authentication for multiple test users
- Complete workflow progression testing
- Status verification at each stage
- Comprehensive logging and error handling
- Polling for async operations
- Role-based approval simulation

Author: AI Test Automation Engineer
Version: 1.0.0
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import uuid

import httpx
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration for test environment
@dataclass
class TestConfig:
    """Configuration for E2E test environment."""
    
    # API Configuration
    api_base_url: str = "http://localhost:8000"
    
    # Firebase Configuration  
    firebase_api_key: str = "AIzaSyBSsGH6ihs8GINwee8fBRGI84P3LqbVQ4w"
    firebase_project_id: str = "drfirst-business-case-gen"
    
    # Test User Credentials (Store securely in production)
    initiator_email: str = "test.initiator@drfirst.com"
    initiator_password: str = "TestPassword123!"
    
    prd_approver_email: str = "test.prd.approver@drfirst.com"
    prd_approver_password: str = "TestPassword123!"
    
    sys_design_approver_email: str = "test.developer@drfirst.com"
    sys_design_approver_password: str = "TestPassword123!"
    
    effort_approver_email: str = "test.effort.approver@drfirst.com"
    effort_approver_password: str = "TestPassword123!"
    
    cost_approver_email: str = "test.finance@drfirst.com"
    cost_approver_password: str = "TestPassword123!"
    
    value_approver_email: str = "test.sales@drfirst.com"
    value_approver_password: str = "TestPassword123!"
    
    final_approver_email: str = "test.final.approver@drfirst.com"
    final_approver_password: str = "TestPassword123!"
    
    admin_email: str = "test.admin@drfirst.com"
    admin_password: str = "TestPassword123!"
    
    # Test Configuration
    max_poll_time: int = 300  # 5 minutes max polling
    poll_interval: int = 5    # 5 seconds between polls
    request_timeout: int = 120 # 2 minutes request timeout for agent operations


class WorkflowStatus(Enum):
    """Expected workflow statuses for each stage."""
    
    # Initial
    INTAKE = "INTAKE"
    PRD_DRAFTING = "PRD_DRAFTING"
    PRD_REVIEW = "PRD_REVIEW"
    PRD_APPROVED = "PRD_APPROVED"
    
    # System Design
    SYSTEM_DESIGN_DRAFTING = "SYSTEM_DESIGN_DRAFTING"
    SYSTEM_DESIGN_DRAFTED = "SYSTEM_DESIGN_DRAFTED"
    SYSTEM_DESIGN_PENDING_REVIEW = "SYSTEM_DESIGN_PENDING_REVIEW"
    SYSTEM_DESIGN_APPROVED = "SYSTEM_DESIGN_APPROVED"
    
    # Effort Estimation
    PLANNING_IN_PROGRESS = "PLANNING_IN_PROGRESS"
    PLANNING_COMPLETE = "PLANNING_COMPLETE"
    EFFORT_PENDING_REVIEW = "EFFORT_PENDING_REVIEW"
    EFFORT_APPROVED = "EFFORT_APPROVED"
    
    # Cost Analysis
    COSTING_IN_PROGRESS = "COSTING_IN_PROGRESS"
    COSTING_COMPLETE = "COSTING_COMPLETE"
    COSTING_PENDING_REVIEW = "COSTING_PENDING_REVIEW"
    COSTING_APPROVED = "COSTING_APPROVED"
    
    # Value Analysis
    VALUE_ANALYSIS_IN_PROGRESS = "VALUE_ANALYSIS_IN_PROGRESS"
    VALUE_ANALYSIS_COMPLETE = "VALUE_ANALYSIS_COMPLETE"
    VALUE_PENDING_REVIEW = "VALUE_PENDING_REVIEW"
    VALUE_APPROVED = "VALUE_APPROVED"
    
    # Financial Model
    FINANCIAL_MODEL_IN_PROGRESS = "FINANCIAL_MODEL_IN_PROGRESS"
    FINANCIAL_MODEL_COMPLETE = "FINANCIAL_MODEL_COMPLETE"
    
    # Final Approval
    PENDING_FINAL_APPROVAL = "PENDING_FINAL_APPROVAL"
    APPROVED = "APPROVED"


@dataclass
class WorkflowStep:
    """Represents a single step in the workflow test."""
    
    step_name: str
    user_email: str
    expected_precondition_status: WorkflowStatus
    api_endpoint: str
    http_method: str
    expected_post_status: WorkflowStatus
    payload: Optional[Dict[str, Any]] = None
    description: str = ""
    requires_data_check: bool = True
    data_field: Optional[str] = None


class E2EWorkflowTester:
    """Main E2E workflow test orchestrator."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.session = self._setup_session()
        self.test_case_id: Optional[str] = None
        self.test_results: List[Dict[str, Any]] = []
        
    def _setup_logging(self) -> logging.Logger:
        """Set up comprehensive logging."""
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"logs/e2e_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info("🔧 E2E Workflow Tester initialized")
        return logger
        
    def _setup_session(self) -> requests.Session:
        """Set up requests session with retry strategy."""
        
        session = requests.Session()
        
        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
        
    async def get_id_token(self, email: str, password: str) -> str:
        """Get Firebase ID token for authentication."""
        
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.config.firebase_api_key}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        try:
            response = self.session.post(auth_url, json=payload, timeout=self.config.request_timeout)
            response.raise_for_status()
            
            data = response.json()
            id_token = data.get("idToken")
            
            if not id_token:
                raise ValueError(f"No ID token received for {email}")
                
            self.logger.info(f"✅ Successfully authenticated {email}")
            return id_token
            
        except Exception as e:
            self.logger.error(f"❌ Authentication failed for {email}: {str(e)}")
            raise
            
    async def make_authenticated_request(
        self, 
        method: str, 
        endpoint: str, 
        id_token: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request."""
        
        url = f"{self.config.api_base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=self.config.request_timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=payload, timeout=self.config.request_timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=headers, json=payload, timeout=self.config.request_timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            
            # Handle empty responses
            if response.content:
                return response.json()
            else:
                return {"status": "success", "message": "Request completed successfully"}
                
        except requests.exceptions.HTTPError as e:
            error_details = {
                "status_code": e.response.status_code,
                "response_text": e.response.text
            }
            self.logger.error(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
            raise Exception(f"API request failed: {error_details}")
        except Exception as e:
            self.logger.error(f"❌ Request failed: {str(e)}")
            raise
            
    async def get_case_details(self, case_id: str, id_token: str) -> Dict[str, Any]:
        """Get current case details and status."""
        
        endpoint = f"/api/v1/cases/{case_id}"
        return await self.make_authenticated_request("GET", endpoint, id_token)
        
    async def poll_for_status(
        self, 
        case_id: str, 
        expected_status: WorkflowStatus,
        id_token: str,
        timeout: int = None
    ) -> bool:
        """Poll for expected case status."""
        
        timeout = timeout or self.config.max_poll_time
        start_time = time.time()
        
        self.logger.info(f"🔄 Polling for status '{expected_status.value}' (timeout: {timeout}s)")
        
        while time.time() - start_time < timeout:
            try:
                case_details = await self.get_case_details(case_id, id_token)
                current_status = case_details.get("status")
                
                self.logger.debug(f"Current status: {current_status}")
                
                if current_status == expected_status.value:
                    self.logger.info(f"✅ Status '{expected_status.value}' achieved")
                    return True
                    
                await asyncio.sleep(self.config.poll_interval)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Polling error: {str(e)}")
                await asyncio.sleep(self.config.poll_interval)
                
        self.logger.error(f"❌ Timeout waiting for status '{expected_status.value}'")
        return False
        
    async def verify_case_data(
        self, 
        case_id: str, 
        id_token: str,
        data_field: str
    ) -> bool:
        """Verify that expected data was created/updated."""
        
        try:
            case_details = await self.get_case_details(case_id, id_token)
            
            if data_field in case_details and case_details[data_field]:
                self.logger.info(f"✅ Data verification passed for field '{data_field}'")
                return True
            else:
                self.logger.error(f"❌ Data verification failed for field '{data_field}'")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Data verification error: {str(e)}")
            return False
            
    async def execute_workflow_step(self, step: WorkflowStep) -> bool:
        """Execute a single workflow step."""
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🚀 STEP: {step.step_name}")
        self.logger.info(f"📧 USER: {step.user_email}")
        self.logger.info(f"📝 DESCRIPTION: {step.description}")
        self.logger.info(f"{'='*80}")
        
        step_start_time = time.time()
        
        try:
            # 1. Authenticate user
            self.logger.info(f"🔐 Authenticating user {step.user_email}")
            id_token = await self.get_id_token(step.user_email, self._get_password_for_email(step.user_email))
            
            # 2. Check precondition status
            self.logger.info(f"🔍 Verifying precondition status: {step.expected_precondition_status.value}")
            if not await self.poll_for_status(self.test_case_id, step.expected_precondition_status, id_token, 60):
                raise Exception(f"Precondition not met: expected status {step.expected_precondition_status.value}")
                
            # 3. Execute the API call
            self.logger.info(f"📡 Making {step.http_method} request to {step.api_endpoint}")
            if step.payload:
                self.logger.debug(f"📦 Payload: {json.dumps(step.payload, indent=2)}")
                
            response = await self.make_authenticated_request(
                step.http_method,
                step.api_endpoint.format(case_id=self.test_case_id),
                id_token,
                step.payload
            )
            
            self.logger.info(f"✅ API call successful: {response.get('message', 'No message')}")
            
            # 4. Verify post-condition status
            self.logger.info(f"🎯 Verifying post-condition status: {step.expected_post_status.value}")
            
            # Try with current user token first
            poll_success = await self.poll_for_status(self.test_case_id, step.expected_post_status, id_token)
            
            # If polling failed and we got a permission error, try with admin token
            if not poll_success:
                self.logger.warning(f"⚠️ Polling failed with user {step.user_email}, trying with admin token")
                admin_token = await self.get_id_token(self.config.admin_email, self.config.admin_password)
                poll_success = await self.poll_for_status(self.test_case_id, step.expected_post_status, admin_token)
                
            if not poll_success:
                raise Exception(f"Post-condition not met: expected status {step.expected_post_status.value}")
                
            # 5. Verify data creation if required
            if step.requires_data_check and step.data_field:
                self.logger.info(f"📊 Verifying data creation for field: {step.data_field}")
                if not await self.verify_case_data(self.test_case_id, id_token, step.data_field):
                    raise Exception(f"Data verification failed for field: {step.data_field}")
                    
            # Record success
            step_duration = time.time() - step_start_time
            result = {
                "step_name": step.step_name,
                "user_email": step.user_email,
                "status": "SUCCESS",
                "duration_seconds": round(step_duration, 2),
                "timestamp": datetime.now().isoformat(),
                "api_response": response
            }
            
            self.test_results.append(result)
            self.logger.info(f"✅ STEP COMPLETED SUCCESSFULLY in {step_duration:.2f}s")
            return True
            
        except Exception as e:
            # Record failure
            step_duration = time.time() - step_start_time
            result = {
                "step_name": step.step_name,
                "user_email": step.user_email,
                "status": "FAILED",
                "duration_seconds": round(step_duration, 2),
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
            
            self.test_results.append(result)
            self.logger.error(f"❌ STEP FAILED: {str(e)}")
            return False
            
    def _get_password_for_email(self, email: str) -> str:
        """Get password for given email."""
        
        email_to_password = {
            self.config.initiator_email: self.config.initiator_password,
            self.config.prd_approver_email: self.config.prd_approver_password,
            self.config.sys_design_approver_email: self.config.sys_design_approver_password,
            self.config.effort_approver_email: self.config.effort_approver_password,
            self.config.cost_approver_email: self.config.cost_approver_password,
            self.config.value_approver_email: self.config.value_approver_password,
            self.config.final_approver_email: self.config.final_approver_password,
            self.config.admin_email: self.config.admin_password,
        }
        
        return email_to_password.get(email, "TestPassword123!")
        
    def _get_workflow_steps(self) -> List[WorkflowStep]:
        """Define the complete workflow steps."""
        
        return [
            # Step 1: Initiate Business Case
            WorkflowStep(
                step_name="1. Initiate Business Case",
                user_email=self.config.initiator_email,
                expected_precondition_status=WorkflowStatus.INTAKE,  # Will be set after creation
                api_endpoint="/api/v1/agents/invoke",
                http_method="POST",
                expected_post_status=WorkflowStatus.PRD_DRAFTING,
                payload={
                    "request_type": "initiate_case",
                    "payload": {
                        "problemStatement": "Healthcare providers need a more efficient way to manage patient appointment scheduling and reduce no-shows. Current system requires multiple phone calls and has a 25% no-show rate causing $50K monthly revenue loss.",
                        "projectTitle": "Smart Patient Appointment Management System",
                        "relevantLinks": [
                            {"name": "Current System Analysis", "url": "https://confluence.drfirst.com/current-analysis"},
                            {"name": "Industry Best Practices", "url": "https://confluence.drfirst.com/best-practices"}
                        ]
                    }
                },
                description="Create new business case and generate initial PRD",
                requires_data_check=True,
                data_field="prd_draft"
            ),
            
            # Step 2: Submit PRD for Review
            WorkflowStep(
                step_name="2. Submit PRD for Review",
                user_email=self.config.initiator_email,
                expected_precondition_status=WorkflowStatus.PRD_DRAFTING,
                api_endpoint="/api/v1/cases/{case_id}/submit-prd",
                http_method="POST",
                expected_post_status=WorkflowStatus.PRD_REVIEW,
                description="Submit completed PRD for stakeholder review"
            ),
            
            # Step 3: Approve PRD
            WorkflowStep(
                step_name="3. Approve PRD",
                user_email=self.config.prd_approver_email,
                expected_precondition_status=WorkflowStatus.PRD_REVIEW,
                api_endpoint="/api/v1/cases/{case_id}/prd/approve",
                http_method="POST",
                expected_post_status=WorkflowStatus.SYSTEM_DESIGN_DRAFTED,  # Changed from SYSTEM_DESIGN_DRAFTING
                description="Approve PRD and trigger system design generation"
            ),
            
            # Step 4: Wait for System Design Draft
            WorkflowStep(
                step_name="4. Wait for System Design Draft",
                user_email=self.config.sys_design_approver_email,
                expected_precondition_status=WorkflowStatus.SYSTEM_DESIGN_DRAFTED,
                api_endpoint="/api/v1/cases/{case_id}",  # Just check status
                http_method="GET",
                expected_post_status=WorkflowStatus.SYSTEM_DESIGN_DRAFTED,
                description="Wait for AI agent to complete system design draft",
                requires_data_check=True,
                data_field="system_design_v1_draft"
            ),
            
            # Step 5: Submit System Design for Review
            WorkflowStep(
                step_name="5. Submit System Design for Review",
                user_email=self.config.initiator_email,
                expected_precondition_status=WorkflowStatus.SYSTEM_DESIGN_DRAFTED,
                api_endpoint="/api/v1/cases/{case_id}/system-design/submit",
                http_method="POST",
                expected_post_status=WorkflowStatus.SYSTEM_DESIGN_PENDING_REVIEW,
                description="Submit system design for technical review"
            ),
            
            # Step 6: Approve System Design
            WorkflowStep(
                step_name="6. Approve System Design",
                user_email=self.config.effort_approver_email,  # Use TECHNICAL_ARCHITECT role
                expected_precondition_status=WorkflowStatus.SYSTEM_DESIGN_PENDING_REVIEW,
                api_endpoint="/api/v1/cases/{case_id}/system-design/approve",
                http_method="POST",
                expected_post_status=WorkflowStatus.PLANNING_COMPLETE,
                description="Approve system design and trigger effort estimation"
            ),
            
            # Step 7: Submit Effort Estimate for Review
            WorkflowStep(
                step_name="7. Submit Effort Estimate for Review",
                user_email=self.config.initiator_email,
                expected_precondition_status=WorkflowStatus.PLANNING_COMPLETE,
                api_endpoint="/api/v1/cases/{case_id}/effort-estimate/submit",
                http_method="POST",
                expected_post_status=WorkflowStatus.EFFORT_PENDING_REVIEW,
                description="Submit effort estimates for stakeholder review",
                requires_data_check=True,
                data_field="effort_estimate_v1"
            ),
            
            # Step 8: Approve Effort Estimate
            WorkflowStep(
                step_name="8. Approve Effort Estimate",
                user_email=self.config.effort_approver_email,
                expected_precondition_status=WorkflowStatus.EFFORT_PENDING_REVIEW,
                api_endpoint="/api/v1/cases/{case_id}/effort-estimate/approve",
                http_method="POST",
                expected_post_status=WorkflowStatus.COSTING_PENDING_REVIEW,
                description="Approve effort estimates and trigger cost analysis"
            ),
            
            # Step 9: Approve Cost Estimate
            WorkflowStep(
                step_name="9. Approve Cost Estimate",
                user_email=self.config.cost_approver_email,
                expected_precondition_status=WorkflowStatus.COSTING_PENDING_REVIEW,
                api_endpoint="/api/v1/cases/{case_id}/cost-estimate/approve",
                http_method="POST",
                expected_post_status=WorkflowStatus.VALUE_PENDING_REVIEW,
                description="Approve cost estimates and trigger value analysis",
                requires_data_check=True,
                data_field="cost_estimate_v1"
            ),
            
            # Step 10: Approve Value Projection
            WorkflowStep(
                step_name="10. Approve Value Projection",
                user_email=self.config.value_approver_email,
                expected_precondition_status=WorkflowStatus.VALUE_PENDING_REVIEW,
                api_endpoint="/api/v1/cases/{case_id}/value-projection/approve",
                http_method="POST",
                expected_post_status=WorkflowStatus.FINANCIAL_MODEL_COMPLETE,
                description="Approve value projections and trigger financial model",
                requires_data_check=True,
                data_field="value_projection_v1"
            ),
            
            # Step 11: Submit for Final Approval
            WorkflowStep(
                step_name="11. Submit for Final Approval",
                user_email=self.config.initiator_email,
                expected_precondition_status=WorkflowStatus.FINANCIAL_MODEL_COMPLETE,
                api_endpoint="/api/v1/cases/{case_id}/submit-final",
                http_method="POST",
                expected_post_status=WorkflowStatus.PENDING_FINAL_APPROVAL,
                description="Submit complete business case for final approval",
                requires_data_check=True,
                data_field="financial_summary_v1"
            ),
            
            # Step 12: Final Approval
            WorkflowStep(
                step_name="12. Final Approval",
                user_email=self.config.final_approver_email,
                expected_precondition_status=WorkflowStatus.PENDING_FINAL_APPROVAL,
                api_endpoint="/api/v1/cases/{case_id}/approve-final",
                http_method="POST",
                expected_post_status=WorkflowStatus.APPROVED,
                description="Provide final approval for business case implementation"
            )
        ]
        
    async def run_happy_path_workflow(self) -> bool:
        """Execute the complete happy path workflow."""
        
        self.logger.info("\n" + "🎯" * 40)
        self.logger.info("🚀 STARTING E2E HAPPY PATH WORKFLOW TEST")
        self.logger.info("🎯" * 40)
        
        workflow_start_time = time.time()
        
        try:
            workflow_steps = self._get_workflow_steps()
            
            # Execute first step (case initiation) specially to get case ID
            first_step = workflow_steps[0]
            self.logger.info(f"\n🔄 Executing initial step: {first_step.step_name}")
            
            # Authenticate initiator
            id_token = await self.get_id_token(first_step.user_email, self._get_password_for_email(first_step.user_email))
            
            # Make initiation request
            response = await self.make_authenticated_request(
                first_step.http_method,
                first_step.api_endpoint,
                id_token,
                first_step.payload
            )
            
            # Extract case ID
            self.test_case_id = response.get("caseId")
            if not self.test_case_id:
                raise Exception("No case ID returned from initiation request")
                
            self.logger.info(f"✅ Business case created with ID: {self.test_case_id}")
            
            # Poll for PRD drafting completion
            if not await self.poll_for_status(self.test_case_id, WorkflowStatus.PRD_DRAFTING, id_token):
                raise Exception("PRD drafting not completed in time")
                
            # Record first step success
            self.test_results.append({
                "step_name": first_step.step_name,
                "user_email": first_step.user_email,
                "status": "SUCCESS",
                "duration_seconds": 0,
                "timestamp": datetime.now().isoformat(),
                "case_id": self.test_case_id
            })
            
            # Execute remaining steps
            for step in workflow_steps[1:]:
                if not await self.execute_workflow_step(step):
                    return False
                    
            # Final verification
            self.logger.info(f"\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            final_id_token = await self.get_id_token(self.config.admin_email, self.config.admin_password)
            final_case_details = await self.get_case_details(self.test_case_id, final_id_token)
            
            self.logger.info(f"📊 Final Case Status: {final_case_details.get('status')}")
            self.logger.info(f"📋 Final Case Title: {final_case_details.get('title')}")
            
            workflow_duration = time.time() - workflow_start_time
            self.logger.info(f"⏱️ Total Workflow Duration: {workflow_duration:.2f} seconds")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ WORKFLOW FAILED: {str(e)}")
            return False
            
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        
        successful_steps = [r for r in self.test_results if r["status"] == "SUCCESS"]
        failed_steps = [r for r in self.test_results if r["status"] == "FAILED"]
        
        total_duration = sum(r["duration_seconds"] for r in self.test_results)
        
        report = {
            "test_summary": {
                "test_case_id": self.test_case_id,
                "timestamp": datetime.now().isoformat(),
                "total_steps": len(self.test_results),
                "successful_steps": len(successful_steps),
                "failed_steps": len(failed_steps),
                "success_rate": round(len(successful_steps) / len(self.test_results) * 100, 1) if self.test_results else 0,
                "total_duration_seconds": round(total_duration, 2),
                "overall_result": "PASS" if len(failed_steps) == 0 else "FAIL"
            },
            "step_results": self.test_results,
            "configuration": {
                "api_base_url": self.config.api_base_url,
                "firebase_project_id": self.config.firebase_project_id,
                "test_users_count": 8
            }
        }
        
        # Save report to file
        report_filename = f"logs/e2e_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        self.logger.info(f"📄 Test report saved to: {report_filename}")
        
        return report
        
    def print_test_summary(self, report: Dict[str, Any]):
        """Print formatted test summary to console."""
        
        summary = report["test_summary"]
        
        print("\n" + "="*80)
        print("🎯 E2E WORKFLOW TEST SUMMARY")
        print("="*80)
        print(f"📋 Test Case ID: {summary['test_case_id']}")
        print(f"🕐 Test Duration: {summary['total_duration_seconds']} seconds")
        print(f"📊 Steps Executed: {summary['total_steps']}")
        print(f"✅ Successful: {summary['successful_steps']}")
        print(f"❌ Failed: {summary['failed_steps']}")
        print(f"📈 Success Rate: {summary['success_rate']}%")
        print(f"🏆 Overall Result: {summary['overall_result']}")
        
        if summary['failed_steps'] > 0:
            print("\n❌ FAILED STEPS:")
            failed_steps = [r for r in report["step_results"] if r["status"] == "FAILED"]
            for step in failed_steps:
                print(f"   - {step['step_name']}: {step.get('error', 'Unknown error')}")
                
        print("="*80)


async def main():
    """Main execution function."""
    
    print("🎯 DrFirst Business Case Generator - E2E Workflow Tester")
    print("=" * 80)
    
    # Load configuration (could be from environment variables or config file)
    config = TestConfig()
    
    # Override configuration from environment variables if available
    config.api_base_url = os.getenv("E2E_API_BASE_URL", config.api_base_url)
    config.firebase_api_key = os.getenv("E2E_FIREBASE_API_KEY", config.firebase_api_key)
    
    # Initialize tester
    tester = E2EWorkflowTester(config)
    
    try:
        # Run the complete workflow
        success = await tester.run_happy_path_workflow()
        
        # Generate and display report
        report = tester.generate_test_report()
        tester.print_test_summary(report)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        tester.logger.info("🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        tester.logger.error(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
        
    # Run the test
    asyncio.run(main()) 