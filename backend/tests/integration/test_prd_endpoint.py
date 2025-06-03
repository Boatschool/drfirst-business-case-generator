"""
Integration tests for PRD update endpoint.
Tests the full flow including authentication, authorization, and Firestore operations.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.api.v1.case_routes import update_prd_draft, PrdUpdateRequest


class TestPrdUpdateEndpoint:
    """Integration tests for the PRD update endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user."""
        return {"uid": "test-user-123", "email": "test@example.com"}

    @pytest.fixture
    def mock_case_data(self):
        """Mock business case data."""
        return {
            "case_id": "test-case-123",
            "user_id": "test-user-123",
            "title": "Test Business Case",
            "problem_statement": "Test problem",
            "status": "PRD_DRAFTING",
            "prd_draft": {
                "title": "Original PRD - Draft",
                "content_markdown": "# Original PRD\n\nOriginal content",
                "version": "1.0.0"
            },
            "history": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

    @pytest.fixture
    def prd_update_request(self):
        """Valid PRD update request."""
        return PrdUpdateRequest(
            content_markdown="# Updated PRD\n\nThis is the updated content."
        )

    @pytest.mark.asyncio
    async def test_successful_prd_update(self, mock_user, mock_case_data, prd_update_request):
        """Test successful PRD update with proper authentication and authorization."""
        case_id = "test-case-123"
        
        # Mock Firestore operations
        with patch('app.api.v1.case_routes.firestore.Client') as mock_firestore:
            mock_db = Mock()
            mock_firestore.return_value = mock_db
            
            # Mock document reference and snapshot
            mock_doc_ref = Mock()
            mock_db.collection.return_value.document.return_value = mock_doc_ref
            
            mock_doc_snapshot = Mock()
            mock_doc_snapshot.exists = True
            mock_doc_snapshot.to_dict.return_value = mock_case_data
            
            # Mock asyncio.to_thread for get operation
            with patch('app.api.v1.case_routes.asyncio.to_thread') as mock_to_thread:
                mock_to_thread.side_effect = [mock_doc_snapshot, None]  # get, update
                
                # Call the endpoint function
                result = await update_prd_draft(case_id, prd_update_request, mock_user)
                
                # Verify the result
                assert result["message"] == "PRD draft updated successfully"
                assert result["updated_prd_draft"]["content_markdown"] == prd_update_request.content_markdown
                assert result["updated_prd_draft"]["title"] == "Test Business Case - Draft"
                assert result["updated_prd_draft"]["version"] == "1.0.0"
                
                # Verify Firestore operations were called correctly
                mock_db.collection.assert_called_with("businessCases")
                mock_db.collection().document.assert_called_with(case_id)
                
                # Verify update was called with correct data
                assert mock_to_thread.call_count == 2  # get and update calls
                update_call_args = mock_to_thread.call_args_list[1]
                assert "prd_draft" in str(update_call_args)
                assert "updated_at" in str(update_call_args)
                assert "history" in str(update_call_args)

    @pytest.mark.asyncio
    async def test_case_not_found(self, mock_user, prd_update_request):
        """Test that 404 is returned when case doesn't exist."""
        case_id = "nonexistent-case"
        
        with patch('app.api.v1.case_routes.firestore.Client') as mock_firestore:
            mock_db = Mock()
            mock_firestore.return_value = mock_db
            
            mock_doc_ref = Mock()
            mock_db.collection.return_value.document.return_value = mock_doc_ref
            
            mock_doc_snapshot = Mock()
            mock_doc_snapshot.exists = False
            
            with patch('app.api.v1.case_routes.asyncio.to_thread', return_value=mock_doc_snapshot):
                with pytest.raises(HTTPException) as exc_info:
                    await update_prd_draft(case_id, prd_update_request, mock_user)
                
                assert exc_info.value.status_code == 404
                assert "not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_unauthorized_user(self, mock_case_data, prd_update_request):
        """Test that 403 is returned when user doesn't own the case."""
        case_id = "test-case-123"
        different_user = {"uid": "different-user-456", "email": "different@example.com"}
        
        with patch('app.api.v1.case_routes.firestore.Client') as mock_firestore:
            mock_db = Mock()
            mock_firestore.return_value = mock_db
            
            mock_doc_ref = Mock()
            mock_db.collection.return_value.document.return_value = mock_doc_ref
            
            mock_doc_snapshot = Mock()
            mock_doc_snapshot.exists = True
            mock_doc_snapshot.to_dict.return_value = mock_case_data
            
            with patch('app.api.v1.case_routes.asyncio.to_thread', return_value=mock_doc_snapshot):
                with pytest.raises(HTTPException) as exc_info:
                    await update_prd_draft(case_id, prd_update_request, different_user)
                
                assert exc_info.value.status_code == 403
                assert "permission" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_missing_user_id_in_token(self, mock_case_data, prd_update_request):
        """Test that 401 is returned when user ID is missing from token."""
        case_id = "test-case-123"
        invalid_user = {"email": "test@example.com"}  # Missing uid
        
        with pytest.raises(HTTPException) as exc_info:
            await update_prd_draft(case_id, prd_update_request, invalid_user)
        
        assert exc_info.value.status_code == 401
        assert "User ID not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_empty_case_data(self, mock_user, prd_update_request):
        """Test that 404 is returned when case data is empty."""
        case_id = "test-case-123"
        
        with patch('app.api.v1.case_routes.firestore.Client') as mock_firestore:
            mock_db = Mock()
            mock_firestore.return_value = mock_db
            
            mock_doc_ref = Mock()
            mock_db.collection.return_value.document.return_value = mock_doc_ref
            
            mock_doc_snapshot = Mock()
            mock_doc_snapshot.exists = True
            mock_doc_snapshot.to_dict.return_value = None
            
            with patch('app.api.v1.case_routes.asyncio.to_thread', return_value=mock_doc_snapshot):
                with pytest.raises(HTTPException) as exc_info:
                    await update_prd_draft(case_id, prd_update_request, mock_user)
                
                assert exc_info.value.status_code == 404
                assert "data is empty" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_firestore_error_handling(self, mock_user, mock_case_data, prd_update_request):
        """Test that 500 is returned when Firestore operations fail."""
        case_id = "test-case-123"
        
        with patch('app.api.v1.case_routes.firestore.Client') as mock_firestore:
            mock_db = Mock()
            mock_firestore.return_value = mock_db
            
            mock_doc_ref = Mock()
            mock_db.collection.return_value.document.return_value = mock_doc_ref
            
            mock_doc_snapshot = Mock()
            mock_doc_snapshot.exists = True
            mock_doc_snapshot.to_dict.return_value = mock_case_data
            
            # Mock firestore error during update
            with patch('app.api.v1.case_routes.asyncio.to_thread') as mock_to_thread:
                mock_to_thread.side_effect = [mock_doc_snapshot, Exception("Firestore error")]
                
                with pytest.raises(HTTPException) as exc_info:
                    await update_prd_draft(case_id, prd_update_request, mock_user)
                
                assert exc_info.value.status_code == 500
                assert "Failed to update PRD draft" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_prd_versioning(self, mock_user, prd_update_request):
        """Test that PRD versioning works correctly."""
        case_id = "test-case-123"
        mock_case_data = {
            "case_id": case_id,
            "user_id": mock_user["uid"],
            "title": "Test Case",
            "prd_draft": {
                "title": "Existing PRD - Draft",
                "content_markdown": "Old content",
                "version": "2.0.0"  # Existing version
            }
        }
        
        with patch('app.api.v1.case_routes.firestore.Client') as mock_firestore:
            mock_db = Mock()
            mock_firestore.return_value = mock_db
            
            mock_doc_ref = Mock()
            mock_db.collection.return_value.document.return_value = mock_doc_ref
            
            mock_doc_snapshot = Mock()
            mock_doc_snapshot.exists = True
            mock_doc_snapshot.to_dict.return_value = mock_case_data
            
            with patch('app.api.v1.case_routes.asyncio.to_thread') as mock_to_thread:
                mock_to_thread.side_effect = [mock_doc_snapshot, None]
                
                result = await update_prd_draft(case_id, prd_update_request, mock_user)
                
                # Should preserve existing version
                assert result["updated_prd_draft"]["version"] == "2.0.0"

    @pytest.mark.asyncio
    async def test_history_entry_creation(self, mock_user, mock_case_data, prd_update_request):
        """Test that history entry is created correctly."""
        case_id = "test-case-123"
        
        with patch('app.api.v1.case_routes.firestore.Client') as mock_firestore:
            mock_db = Mock()
            mock_firestore.return_value = mock_db
            
            mock_doc_ref = Mock()
            mock_db.collection.return_value.document.return_value = mock_doc_ref
            
            mock_doc_snapshot = Mock()
            mock_doc_snapshot.exists = True
            mock_doc_snapshot.to_dict.return_value = mock_case_data
            
            with patch('app.api.v1.case_routes.asyncio.to_thread') as mock_to_thread:
                mock_to_thread.side_effect = [mock_doc_snapshot, None]
                
                with patch('app.api.v1.case_routes.firestore.ArrayUnion') as mock_array_union:
                    await update_prd_draft(case_id, prd_update_request, mock_user)
                    
                    # Verify ArrayUnion was called for history
                    mock_array_union.assert_called_once()
                    history_entry = mock_array_union.call_args[0][0][0]
                    
                    assert history_entry["source"] == "USER"
                    assert history_entry["messageType"] == "PRD_UPDATE"
                    assert "User updated the PRD draft" in history_entry["content"]
                    assert isinstance(history_entry["timestamp"], datetime)

    @pytest.mark.asyncio
    async def test_case_without_existing_prd(self, mock_user, prd_update_request):
        """Test updating PRD for a case that doesn't have an existing PRD draft."""
        case_id = "test-case-123"
        mock_case_data = {
            "case_id": case_id,
            "user_id": mock_user["uid"],
            "title": "Test Case",
            # No prd_draft field
        }
        
        with patch('app.api.v1.case_routes.firestore.Client') as mock_firestore:
            mock_db = Mock()
            mock_firestore.return_value = mock_db
            
            mock_doc_ref = Mock()
            mock_db.collection.return_value.document.return_value = mock_doc_ref
            
            mock_doc_snapshot = Mock()
            mock_doc_snapshot.exists = True
            mock_doc_snapshot.to_dict.return_value = mock_case_data
            
            with patch('app.api.v1.case_routes.asyncio.to_thread') as mock_to_thread:
                mock_to_thread.side_effect = [mock_doc_snapshot, None]
                
                result = await update_prd_draft(case_id, prd_update_request, mock_user)
                
                # Should create new PRD with default version
                assert result["updated_prd_draft"]["version"] == "1.0.0"
                assert result["updated_prd_draft"]["content_markdown"] == prd_update_request.content_markdown 