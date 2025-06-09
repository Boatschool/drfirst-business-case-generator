"""
Enhanced Logging Test Suite for System Design Workflow.
Tests that verify the diagnostic logging added in Task FIX-WF-3.
"""

import pytest
import pytest_asyncio
import logging
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from app.api.v1.cases.system_design_routes import (
    approve_system_design,
    reject_system_design
)
from app.api.v1.cases.models import SystemDesignRejectRequest
from app.agents.orchestrator_agent import BusinessCaseStatus, OrchestratorAgent
from tests.utils.logging_test_helpers import (
    assert_log_contains,
    assert_log_sequence,
    assert_log_count,
    get_log_messages,
    assert_workflow_logging_sequence,
    LogLevelContext
)


class TestEnhancedSystemDesignLogging:
    """Test suite for enhanced diagnostic logging in system design workflow."""

    @pytest.fixture
    def mock_business_case(self):
        """Create a mock business case for testing."""
        case = Mock()
        case.case_id = "test-case-456"
        case.user_id = "test-user-789"
        case.title = "Test Business Case"
        case.status = BusinessCaseStatus.SYSTEM_DESIGN_PENDING_REVIEW
        case.system_design_v1_draft = {
            "content_markdown": "# Test System Design",
            "generated_by": "ArchitectAgent"
        }
        case.history = []
        return case

    @pytest.fixture
    def mock_developer_user(self):
        """Create a mock developer user."""
        return {
            "uid": "developer-user-123",
            "email": "dev@drfirst.com",
            "custom_claims": {"role": "DEVELOPER"}
        }

    @pytest.fixture
    def mock_firestore_service(self):
        """Create a mock firestore service."""
        service = Mock()
        service.get_business_case = AsyncMock()
        service.update_business_case = AsyncMock()
        return service

    @pytest.fixture
    def system_design_reject_request(self):
        """Create a system design reject request."""
        return SystemDesignRejectRequest(
            reason="Needs better error handling implementation."
        )

    @pytest.mark.asyncio
    async def test_system_design_approval_logging_sequence(
        self, mock_business_case, mock_developer_user, mock_firestore_service, caplog
    ):
        """Test that system design approval generates the correct logging sequence."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_system_design_approval = AsyncMock(return_value={
                "status": "success",
                "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            # Ensure INFO level logging is captured
            with LogLevelContext('app.api.v1.cases.system_design_routes', 'INFO'):
                # Execute
                await approve_system_design(
                    case_id="test-case-456",
                    current_user=mock_developer_user,
                    firestore_service=mock_firestore_service
                )

            # Verify complete logging sequence using helper
            assert_workflow_logging_sequence(caplog, "test-case-456", "approval")

    @pytest.mark.asyncio
    async def test_system_design_rejection_logging_sequence(
        self, mock_business_case, mock_developer_user, mock_firestore_service, system_design_reject_request, caplog
    ):
        """Test that system design rejection generates the correct logging sequence."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        # Ensure INFO level logging is captured
        with LogLevelContext('app.api.v1.cases.system_design_routes', 'INFO'):
            # Execute
            await reject_system_design(
                case_id="test-case-456",
                reject_request=system_design_reject_request,
                current_user=mock_developer_user,
                firestore_service=mock_firestore_service
            )

        # Verify complete logging sequence using helper
        assert_workflow_logging_sequence(caplog, "test-case-456", "rejection")

    @pytest.mark.asyncio
    async def test_logging_contains_user_information(
        self, mock_business_case, mock_developer_user, mock_firestore_service, caplog
    ):
        """Test that logging contains proper user identification information."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_system_design_approval = AsyncMock(return_value={
                "status": "success",
                "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            with LogLevelContext('app.api.v1.cases.system_design_routes', 'INFO'):
                await approve_system_design(
                    case_id="test-case-456",
                    current_user=mock_developer_user,
                    firestore_service=mock_firestore_service
                )

        # Verify that user email is included in logs
        info_messages = get_log_messages(caplog, "INFO", "app.api.v1.cases.system_design_routes")
        user_related_logs = [msg for msg in info_messages if "dev@drfirst.com" in msg]
        assert len(user_related_logs) >= 1, "User email should appear in at least one log message"

    @pytest.mark.asyncio
    async def test_logging_contains_case_information(
        self, mock_business_case, mock_developer_user, mock_firestore_service, caplog
    ):
        """Test that logging contains proper case identification information."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_system_design_approval = AsyncMock(return_value={
                "status": "success",
                "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            with LogLevelContext('app.api.v1.cases.system_design_routes', 'INFO'):
                await approve_system_design(
                    case_id="test-case-456",
                    current_user=mock_developer_user,
                    firestore_service=mock_firestore_service
                )

        # Verify that case ID appears in all relevant log messages
        info_messages = get_log_messages(caplog, "INFO", "app.api.v1.cases.system_design_routes")
        case_related_logs = [msg for msg in info_messages if "test-case-456" in msg]
        assert len(case_related_logs) >= 4, "Case ID should appear in all main workflow log messages"

    @pytest.mark.asyncio
    async def test_logging_count_for_successful_approval(
        self, mock_business_case, mock_developer_user, mock_firestore_service, caplog
    ):
        """Test that the correct number of log messages are generated for successful approval."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_system_design_approval = AsyncMock(return_value={
                "status": "success",
                "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            with LogLevelContext('app.api.v1.cases.system_design_routes', 'INFO'):
                await approve_system_design(
                    case_id="test-case-456",
                    current_user=mock_developer_user,
                    firestore_service=mock_firestore_service
                )

        # Verify expected number of INFO log messages from our specific logger (6 including effort estimation logs)
        assert_log_count(caplog, "INFO", 6, "app.api.v1.cases.system_design_routes")

    @pytest.mark.asyncio
    async def test_logging_status_transitions_are_detailed(
        self, mock_business_case, mock_developer_user, mock_firestore_service, caplog
    ):
        """Test that status transition logs contain detailed from/to information."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_system_design_approval = AsyncMock(return_value={
                "status": "success",
                "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            with LogLevelContext('app.api.v1.cases.system_design_routes', 'INFO'):
                await approve_system_design(
                    case_id="test-case-456",
                    current_user=mock_developer_user,
                    firestore_service=mock_firestore_service
                )

        # Verify status transition log has both old and new status
        assert_log_contains(
            caplog,
            "INFO",
            "Status transition: SYSTEM_DESIGN_PENDING_REVIEW -> SYSTEM_DESIGN_APPROVED for case test-case-456",
            "app.api.v1.cases.system_design_routes"
        )

    @pytest.mark.asyncio
    async def test_logging_with_different_log_levels(
        self, mock_business_case, mock_developer_user, mock_firestore_service, caplog
    ):
        """Test logging behavior at different log levels."""
        # Setup  
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_system_design_approval = AsyncMock(return_value={
                "status": "success",
                "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            # Test with DEBUG level - should capture INFO messages too
            with LogLevelContext('app.api.v1.cases.system_design_routes', 'DEBUG'):
                await approve_system_design(
                    case_id="test-case-456",
                    current_user=mock_developer_user,
                    firestore_service=mock_firestore_service
                )

                 # Should still capture all INFO messages (6 including effort estimation logs)
        assert_log_count(caplog, "INFO", 6, "app.api.v1.cases.system_design_routes")

    @pytest.mark.asyncio
    async def test_orchestrator_method_call_logging(
        self, mock_business_case, mock_developer_user, mock_firestore_service, caplog
    ):
        """Test that orchestrator method calls are properly logged."""
        # Setup
        mock_firestore_service.get_business_case.return_value = mock_business_case
        mock_firestore_service.update_business_case.return_value = True

        with patch('app.agents.orchestrator_agent.OrchestratorAgent') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator.handle_system_design_approval = AsyncMock(return_value={
                "status": "success",
                "new_status": BusinessCaseStatus.PLANNING_COMPLETE.value
            })
            mock_orchestrator_class.return_value = mock_orchestrator

            with LogLevelContext('app.api.v1.cases.system_design_routes', 'INFO'):
                await approve_system_design(
                    case_id="test-case-456",
                    current_user=mock_developer_user,
                    firestore_service=mock_firestore_service
                )

        # Verify orchestrator method call is logged
        assert_log_contains(
            caplog,
            "INFO",
            "Calling orchestrator\\.handle_system_design_approval\\(\\) for case test-case-456",
            "app.api.v1.cases.system_design_routes"
        )


class TestOrchestratorAgentLogging:
    """Test suite for enhanced logging in OrchestratorAgent."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock Firestore database."""
        db = Mock()
        return db

    @pytest.fixture
    def mock_case_doc_ref(self):
        """Create a mock Firestore document reference."""
        doc_ref = Mock()
        return doc_ref

    @pytest.fixture  
    def mock_case_data(self):
        """Create mock case data."""
        return {
            "status": BusinessCaseStatus.SYSTEM_DESIGN_APPROVED.value,
            "title": "Test Case",
            "system_design_v1_draft": {
                "content_markdown": "# Test Design"
            },
            "prd_draft": {
                "content_markdown": "# Test PRD"
            }
        }

    @pytest.mark.asyncio
    async def test_orchestrator_status_validation_logging(
        self, mock_db, mock_case_doc_ref, mock_case_data, caplog
    ):
        """Test that orchestrator logs status validation checks."""
        # Skip this test for now - requires implementation of actual logging in OrchestratorAgent
        pytest.skip("Orchestrator agent logging implementation pending - requires handle_system_design_approval method")

    @pytest.mark.asyncio
    async def test_orchestrator_agent_invocation_logging(
        self, mock_db, mock_case_doc_ref, mock_case_data, caplog
    ):
        """Test that orchestrator logs agent invocations and responses."""
        # Skip this test for now - requires implementation of actual logging in OrchestratorAgent
        pytest.skip("Orchestrator agent logging implementation pending - requires handle_system_design_approval method")

    @pytest.mark.asyncio
    async def test_orchestrator_status_transition_logging(
        self, mock_db, mock_case_doc_ref, mock_case_data, caplog
    ):
        """Test that orchestrator logs status transitions in detail."""
        # Skip this test for now - requires implementation of actual logging in OrchestratorAgent
        pytest.skip("Orchestrator agent logging implementation pending - requires handle_system_design_approval method") 