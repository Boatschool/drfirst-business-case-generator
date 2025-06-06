"""
Unit tests for FirestoreService
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from app.services.firestore_service import (
    FirestoreService, 
    FirestoreServiceError, 
    DocumentNotFoundError
)
from app.models.firestore_models import User, BusinessCase, Job, JobStatus, UserRole, BusinessCaseRequest


class TestFirestoreService:
    """Test cases for FirestoreService"""

    @pytest.fixture
    def mock_db(self):
        """Mock database client"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.collection.return_value = mock_collection
        return mock_db

    @pytest.fixture
    def firestore_service(self, mock_db):
        """FirestoreService instance with mocked database"""
        return FirestoreService(db=mock_db)

    @pytest.fixture
    def sample_user(self):
        """Sample user for testing"""
        return User(
            uid="test-uid-123",
            email="test@example.com",
            display_name="Test User",
            systemRole=UserRole.USER,
            is_active=True
        )

    @pytest.fixture
    def sample_business_case_request(self):
        """Sample business case request for testing"""
        return BusinessCaseRequest(
            title="Test Business Case",
            description="Test description",
            requester_uid="test-uid-123",
            priority="high"
        )

    @pytest.fixture
    def sample_business_case(self, sample_business_case_request):
        """Sample business case for testing"""
        return BusinessCase(
            id="test-case-123",
            request_data=sample_business_case_request,
            status=JobStatus.PENDING
        )

    @pytest.fixture
    def sample_job(self):
        """Sample job for testing"""
        return Job(
            id="test-job-123",
            job_type="business_case_generation",
            status=JobStatus.PENDING,
            user_uid="test-uid-123",
            progress=0
        )

    # User tests
    @pytest.mark.asyncio
    async def test_create_user_success(self, firestore_service, sample_user, mock_db):
        """Test successful user creation"""
        mock_doc_ref = Mock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = None
            
            result = await firestore_service.create_user(sample_user)
            
            assert result is True
            mock_to_thread.assert_called_once()
            mock_db.collection.assert_called_with("users")

    @pytest.mark.asyncio
    async def test_create_user_error(self, firestore_service, sample_user, mock_db):
        """Test user creation error handling"""
        mock_db.collection.side_effect = Exception("Database error")
        
        with pytest.raises(FirestoreServiceError) as exc_info:
            await firestore_service.create_user(sample_user)
        
        assert "Failed to create user" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_success(self, firestore_service, sample_user, mock_db):
        """Test successful user retrieval"""
        mock_doc_ref = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "uid": sample_user.uid,
            "email": sample_user.email,
            "display_name": sample_user.display_name,
            "systemRole": sample_user.systemRole.value,
            "is_active": sample_user.is_active,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = mock_doc
            
            result = await firestore_service.get_user(sample_user.uid)
            
            assert result is not None
            assert result.uid == sample_user.uid
            assert result.email == sample_user.email
            mock_to_thread.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, firestore_service, mock_db):
        """Test user not found scenario"""
        mock_doc_ref = Mock()
        mock_doc = Mock()
        mock_doc.exists = False
        
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = mock_doc
            
            result = await firestore_service.get_user("nonexistent-uid")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, firestore_service, sample_user, mock_db):
        """Test successful user retrieval by email"""
        mock_query = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "uid": sample_user.uid,
            "email": sample_user.email,
            "display_name": sample_user.display_name,
            "systemRole": sample_user.systemRole.value,
            "is_active": sample_user.is_active,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        mock_db.collection.return_value.where.return_value = mock_query
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = [mock_doc]
            
            result = await firestore_service.get_user_by_email(sample_user.email)
            
            assert result is not None
            assert result.email == sample_user.email

    @pytest.mark.asyncio
    async def test_update_user_success(self, firestore_service, mock_db):
        """Test successful user update"""
        mock_doc_ref = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        updates = {"display_name": "Updated Name"}
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [mock_doc, None]  # get, then update
            
            result = await firestore_service.update_user("test-uid", updates)
            
            assert result is True
            assert mock_to_thread.call_count == 2

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, firestore_service, mock_db):
        """Test user update when user doesn't exist"""
        mock_doc_ref = Mock()
        mock_doc = Mock()
        mock_doc.exists = False
        
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = mock_doc
            
            with pytest.raises(DocumentNotFoundError):
                await firestore_service.update_user("nonexistent-uid", {"test": "value"})

    @pytest.mark.asyncio
    async def test_list_users_success(self, firestore_service, sample_user, mock_db):
        """Test successful user listing"""
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "uid": sample_user.uid,
            "email": sample_user.email,
            "display_name": sample_user.display_name,
            "systemRole": sample_user.systemRole.value,
            "is_active": sample_user.is_active,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        mock_db.collection.return_value = Mock()
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = [mock_doc]
            
            result = await firestore_service.list_users()
            
            assert len(result) == 1
            assert result[0].uid == sample_user.uid

    @pytest.mark.asyncio
    async def test_delete_user_success(self, firestore_service, mock_db):
        """Test successful user deletion"""
        mock_doc_ref = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [mock_doc, None]  # get, then delete
            
            result = await firestore_service.delete_user("test-uid")
            
            assert result is True
            assert mock_to_thread.call_count == 2

    # Business Case tests
    @pytest.mark.asyncio
    async def test_create_business_case_success(self, firestore_service, sample_business_case, mock_db):
        """Test successful business case creation"""
        mock_doc_ref = Mock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = None
            
            result = await firestore_service.create_business_case(sample_business_case)
            
            assert result == sample_business_case.id
            mock_to_thread.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_business_case_auto_id(self, firestore_service, sample_business_case, mock_db):
        """Test business case creation with auto-generated ID"""
        sample_business_case.id = None
        mock_doc_ref = Mock()
        mock_doc_ref.id = "auto-generated-id"
        
        mock_db.collection.return_value = Mock()
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = (None, mock_doc_ref)
            
            result = await firestore_service.create_business_case(sample_business_case)
            
            assert result == "auto-generated-id"

    @pytest.mark.asyncio
    async def test_get_business_case_success(self, firestore_service, sample_business_case, mock_db):
        """Test successful business case retrieval"""
        mock_doc_ref = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "request_data": {
                "title": sample_business_case.request_data.title,
                "description": sample_business_case.request_data.description,
                "requester_uid": sample_business_case.request_data.requester_uid,
                "priority": sample_business_case.request_data.priority
            },
            "status": sample_business_case.status.value,
            "generated_content": {},
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "generated_by_agents": []
        }
        
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = mock_doc
            
            result = await firestore_service.get_business_case(sample_business_case.id)
            
            assert result is not None
            assert result.id == sample_business_case.id
            assert result.request_data.title == sample_business_case.request_data.title

    @pytest.mark.asyncio
    async def test_update_business_case_success(self, firestore_service, mock_db):
        """Test successful business case update"""
        mock_doc_ref = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        updates = {"status": "in_progress"}
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [mock_doc, None]  # get, then update
            
            result = await firestore_service.update_business_case("test-case-id", updates)
            
            assert result is True

    @pytest.mark.asyncio
    async def test_list_business_cases_for_user_success(self, firestore_service, sample_business_case, mock_db):
        """Test successful business case listing for user"""
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.id = sample_business_case.id
        mock_doc.to_dict.return_value = {
            "request_data": {
                "title": sample_business_case.request_data.title,
                "description": sample_business_case.request_data.description,
                "requester_uid": sample_business_case.request_data.requester_uid,
                "priority": sample_business_case.request_data.priority
            },
            "status": sample_business_case.status.value,
            "generated_content": {},
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "generated_by_agents": []
        }
        
        mock_query = Mock()
        mock_db.collection.return_value.where.return_value = mock_query
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = [mock_doc]
            
            result = await firestore_service.list_business_cases_for_user("test-uid")
            
            assert len(result) == 1
            assert result[0].id == sample_business_case.id

    @pytest.mark.asyncio
    async def test_delete_business_case_success(self, firestore_service, mock_db):
        """Test successful business case deletion"""
        mock_doc_ref = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [mock_doc, None]  # get, then delete
            
            result = await firestore_service.delete_business_case("test-case-id")
            
            assert result is True

    # Job tests
    @pytest.mark.asyncio
    async def test_create_job_success(self, firestore_service, sample_job, mock_db):
        """Test successful job creation"""
        mock_doc_ref = Mock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = None
            
            result = await firestore_service.create_job(sample_job)
            
            assert result == sample_job.id
            mock_to_thread.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_job_success(self, firestore_service, sample_job, mock_db):
        """Test successful job retrieval"""
        mock_doc_ref = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "job_type": sample_job.job_type,
            "status": sample_job.status.value,
            "user_uid": sample_job.user_uid,
            "progress": sample_job.progress,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "metadata": {}
        }
        
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = mock_doc
            
            result = await firestore_service.get_job(sample_job.id)
            
            assert result is not None
            assert result.id == sample_job.id
            assert result.job_type == sample_job.job_type

    @pytest.mark.asyncio
    async def test_update_job_success(self, firestore_service, mock_db):
        """Test successful job update"""
        mock_doc_ref = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        updates = {"status": "completed", "progress": 100}
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [mock_doc, None]  # get, then update
            
            result = await firestore_service.update_job("test-job-id", updates)
            
            assert result is True

    @pytest.mark.asyncio
    async def test_list_jobs_for_user_success(self, firestore_service, sample_job, mock_db):
        """Test successful job listing for user"""
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.id = sample_job.id
        mock_doc.to_dict.return_value = {
            "job_type": sample_job.job_type,
            "status": sample_job.status.value,
            "user_uid": sample_job.user_uid,
            "progress": sample_job.progress,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "metadata": {}
        }
        
        mock_query = Mock()
        mock_db.collection.return_value.where.return_value = mock_query
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = [mock_doc]
            
            result = await firestore_service.list_jobs_for_user("test-uid")
            
            assert len(result) == 1
            assert result[0].id == sample_job.id

    @pytest.mark.asyncio
    async def test_list_jobs_by_status_success(self, firestore_service, sample_job, mock_db):
        """Test successful job listing by status"""
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.id = sample_job.id
        mock_doc.to_dict.return_value = {
            "job_type": sample_job.job_type,
            "status": sample_job.status.value,
            "user_uid": sample_job.user_uid,
            "progress": sample_job.progress,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "metadata": {}
        }
        
        mock_query = Mock()
        mock_db.collection.return_value.where.return_value = mock_query
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = [mock_doc]
            
            result = await firestore_service.list_jobs_by_status(JobStatus.PENDING)
            
            assert len(result) == 1
            assert result[0].status == JobStatus.PENDING

    @pytest.mark.asyncio
    async def test_delete_job_success(self, firestore_service, mock_db):
        """Test successful job deletion"""
        mock_doc_ref = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = [mock_doc, None]  # get, then delete
            
            result = await firestore_service.delete_job("test-job-id")
            
            assert result is True

    # Error handling tests
    @pytest.mark.asyncio
    async def test_service_error_propagation(self, firestore_service, sample_user, mock_db):
        """Test that service errors are properly propagated"""
        mock_db.collection.side_effect = Exception("Network error")
        
        with pytest.raises(FirestoreServiceError) as exc_info:
            await firestore_service.create_user(sample_user)
        
        assert "Failed to create user" in str(exc_info.value)
        assert "Network error" in str(exc_info.value)

    def test_initialization_with_custom_db(self):
        """Test FirestoreService initialization with custom database"""
        mock_db = Mock()
        service = FirestoreService(db=mock_db)
        
        assert service._db == mock_db
        assert service.users_collection == "users"
        assert service.business_cases_collection == "business_cases"
        assert service.jobs_collection == "jobs"

    def test_initialization_with_default_db(self):
        """Test FirestoreService initialization with default database"""
        with patch('app.services.firestore_service.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            service = FirestoreService()
            
            assert service._db == mock_db
            mock_get_db.assert_called_once() 