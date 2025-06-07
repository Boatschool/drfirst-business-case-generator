"""
Firestore service for database operations
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.core.dependencies import get_db
from app.core.database import DatabaseClient
from app.core.exceptions import (
    DatabaseError, UserNotFoundError, BusinessCaseNotFoundError, 
    JobNotFoundError, ServiceError
)
from app.models.firestore_models import User, BusinessCase, Job, JobStatus, UserRole

# Import BusinessCaseData from orchestrator_agent  
from app.agents.orchestrator_agent import BusinessCaseData


# Legacy exception classes for backward compatibility
class FirestoreServiceError(ServiceError):
    """Base exception for Firestore service errors"""
    def __init__(self, detail: str, context: Dict[str, Any] = None):
        super().__init__(service_name="Firestore", detail=detail, context=context)


class DocumentNotFoundError(FirestoreServiceError):
    """Raised when a document is not found - legacy compatibility"""
    pass


class FirestoreService:
    """Service for Firestore database operations"""

    def __init__(self, db: Optional[DatabaseClient] = None):
        self.logger = logging.getLogger(__name__)
        self._db_instance = db
        self._db_initialized = False
        
        # Collection names from settings
        self.users_collection = settings.firestore_collection_users
        self.business_cases_collection = settings.firestore_collection_business_cases
        self.jobs_collection = settings.firestore_collection_jobs
    
    @property
    def _db(self):
        """Lazy initialization of database client"""
        if not self._db_initialized:
            self._db_instance = self._db_instance if self._db_instance is not None else get_db()
            self._db_initialized = True
            self.logger.info("FirestoreService initialized successfully")
        return self._db_instance

    # User operations
    async def create_user(self, user: User) -> bool:
        """Create a new user in Firestore"""
        try:
            self.logger.info(f"Creating user with UID: {user.uid}")
            
            # Update timestamps
            user.created_at = datetime.now(timezone.utc)
            user.updated_at = datetime.now(timezone.utc)
            
            user_ref = self._db.collection(self.users_collection).document(user.uid)
            user_data = user.model_dump(exclude_none=True)
            
            # Convert datetime objects to ISO strings for Firestore
            if 'created_at' in user_data:
                user_data['created_at'] = user_data['created_at'].isoformat()
            if 'updated_at' in user_data:
                user_data['updated_at'] = user_data['updated_at'].isoformat()
            if 'last_login' in user_data and user_data['last_login']:
                user_data['last_login'] = user_data['last_login'].isoformat()
            
            await asyncio.to_thread(user_ref.set, user_data)
            
            self.logger.info(f"User {user.uid} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating user {user.uid}: {str(e)}")
            raise DatabaseError(
                operation="create user",
                detail=str(e),
                context={"user_uid": user.uid}
            )

    async def get_user(self, uid: str) -> Optional[User]:
        """Get user by UID"""
        try:
            self.logger.debug(f"Retrieving user with UID: {uid}")
            
            user_ref = self._db.collection(self.users_collection).document(uid)
            doc = await asyncio.to_thread(user_ref.get)
            
            if not doc.exists:
                self.logger.debug(f"User {uid} not found")
                return None
                
            user_data = doc.to_dict()
            
            # Convert ISO strings back to datetime objects
            if 'created_at' in user_data and isinstance(user_data['created_at'], str):
                user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
            if 'updated_at' in user_data and isinstance(user_data['updated_at'], str):
                user_data['updated_at'] = datetime.fromisoformat(user_data['updated_at'])
            if 'last_login' in user_data and user_data['last_login']:
                user_data['last_login'] = datetime.fromisoformat(user_data['last_login'])
            
            user = User(**user_data)
            self.logger.debug(f"User {uid} retrieved successfully")
            return user
            
        except Exception as e:
            self.logger.error(f"Error retrieving user {uid}: {str(e)}")
            raise DatabaseError(
                operation="get user",
                detail=str(e),
                context={"user_uid": uid}
            )

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        try:
            self.logger.debug(f"Retrieving user with email: {email}")
            
            users_ref = self._db.collection(self.users_collection)
            query = users_ref.where("email", "==", email)
            docs = await asyncio.to_thread(query.stream)
            
            for doc in docs:
                if doc.exists:
                    user_data = doc.to_dict()
                    
                    # Convert ISO strings back to datetime objects
                    if 'created_at' in user_data and isinstance(user_data['created_at'], str):
                        user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
                    if 'updated_at' in user_data and isinstance(user_data['updated_at'], str):
                        user_data['updated_at'] = datetime.fromisoformat(user_data['updated_at'])
                    if 'last_login' in user_data and user_data['last_login']:
                        user_data['last_login'] = datetime.fromisoformat(user_data['last_login'])
                    
                    user = User(**user_data)
                    self.logger.debug(f"User with email {email} found")
                    return user
            
            self.logger.debug(f"User with email {email} not found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving user by email {email}: {str(e)}")
            raise FirestoreServiceError(f"Failed to retrieve user by email: {str(e)}")

    async def update_user(self, uid: str, updates: Dict[str, Any]) -> bool:
        """Update user information"""
        try:
            self.logger.info(f"Updating user {uid}")
            
            # Add updated timestamp
            updates['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            # Convert datetime objects to ISO strings if present
            for key, value in updates.items():
                if isinstance(value, datetime):
                    updates[key] = value.isoformat()
            
            user_ref = self._db.collection(self.users_collection).document(uid)
            
            # Check if user exists first
            doc = await asyncio.to_thread(user_ref.get)
            if not doc.exists:
                raise UserNotFoundError(uid)
            
            await asyncio.to_thread(user_ref.update, updates)
            
            self.logger.info(f"User {uid} updated successfully")
            return True
            
        except UserNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating user {uid}: {str(e)}")
            raise DatabaseError(
                operation="update user",
                detail=str(e),
                context={"user_uid": uid}
            )

    async def list_users(self) -> List[User]:
        """List all users (for admin functionality)"""
        try:
            self.logger.debug("Retrieving all users")
            
            users_ref = self._db.collection(self.users_collection)
            docs = await asyncio.to_thread(users_ref.stream)
            
            users = []
            for doc in docs:
                if doc.exists:
                    user_data = doc.to_dict()
                    
                    # Convert ISO strings back to datetime objects
                    if 'created_at' in user_data and isinstance(user_data['created_at'], str):
                        user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
                    if 'updated_at' in user_data and isinstance(user_data['updated_at'], str):
                        user_data['updated_at'] = datetime.fromisoformat(user_data['updated_at'])
                    if 'last_login' in user_data and user_data['last_login']:
                        user_data['last_login'] = datetime.fromisoformat(user_data['last_login'])
                    
                    users.append(User(**user_data))
            
            self.logger.debug(f"Retrieved {len(users)} users")
            return users
            
        except Exception as e:
            self.logger.error(f"Error listing users: {str(e)}")
            raise FirestoreServiceError(f"Failed to list users: {str(e)}")

    async def delete_user(self, uid: str) -> bool:
        """Delete a user"""
        try:
            self.logger.info(f"Deleting user {uid}")
            
            user_ref = self._db.collection(self.users_collection).document(uid)
            
            # Check if user exists first
            doc = await asyncio.to_thread(user_ref.get)
            if not doc.exists:
                raise DocumentNotFoundError(f"User {uid} not found")
            
            await asyncio.to_thread(user_ref.delete)
            
            self.logger.info(f"User {uid} deleted successfully")
            return True
            
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error deleting user {uid}: {str(e)}")
            raise FirestoreServiceError(f"Failed to delete user: {str(e)}")

    # Business case operations
    async def create_business_case(self, business_case: BusinessCase) -> Optional[str]:
        """Create a new business case"""
        try:
            self.logger.info(f"Creating business case: {business_case.request_data.title}")
            
            # Update timestamps
            business_case.created_at = datetime.now(timezone.utc)
            business_case.updated_at = datetime.now(timezone.utc)
            
            case_data = business_case.model_dump(exclude_none=True)
            
            # Convert datetime objects to ISO strings for Firestore
            if 'created_at' in case_data:
                case_data['created_at'] = case_data['created_at'].isoformat()
            if 'updated_at' in case_data:
                case_data['updated_at'] = case_data['updated_at'].isoformat()
            if 'completed_at' in case_data and case_data['completed_at']:
                case_data['completed_at'] = case_data['completed_at'].isoformat()
            
            # Handle nested datetime objects in request_data
            if 'request_data' in case_data and 'deadline' in case_data['request_data']:
                if case_data['request_data']['deadline']:
                    case_data['request_data']['deadline'] = case_data['request_data']['deadline'].isoformat()
            
            cases_ref = self._db.collection(self.business_cases_collection)
            
            if business_case.id:
                # Use specific ID if provided
                doc_ref = cases_ref.document(business_case.id)
                await asyncio.to_thread(doc_ref.set, case_data)
                case_id = business_case.id
            else:
                # Auto-generate ID
                doc_ref = await asyncio.to_thread(cases_ref.add, case_data)
                case_id = doc_ref[1].id
            
            self.logger.info(f"Business case created with ID: {case_id}")
            return case_id
            
        except Exception as e:
            self.logger.error(f"Error creating business case: {str(e)}")
            raise FirestoreServiceError(f"Failed to create business case: {str(e)}")

    async def get_business_case(self, case_id: str) -> Optional[BusinessCaseData]:
        """Get business case by ID - Returns BusinessCaseData model used by orchestrator agent"""
        try:
            self.logger.debug(f"Retrieving business case: {case_id}")
            
            case_ref = self._db.collection(self.business_cases_collection).document(case_id)
            doc = await asyncio.to_thread(case_ref.get)
            
            if not doc.exists:
                self.logger.debug(f"Business case {case_id} not found")
                return None
                
            case_data = doc.to_dict()
            
            # Convert ISO strings back to datetime objects if needed
            if 'created_at' in case_data and isinstance(case_data['created_at'], str):
                case_data['created_at'] = datetime.fromisoformat(case_data['created_at'])
            if 'updated_at' in case_data and isinstance(case_data['updated_at'], str):
                case_data['updated_at'] = datetime.fromisoformat(case_data['updated_at'])
                
            # Ensure case_id is set correctly
            case_data['case_id'] = case_id
            
            # Try to parse as BusinessCaseData (new format used by orchestrator)
            try:
                business_case = BusinessCaseData(**case_data)
                self.logger.debug(f"Business case {case_id} retrieved successfully as BusinessCaseData")
                return business_case
            except Exception as parse_error:
                self.logger.warning(f"Failed to parse as BusinessCaseData: {parse_error}")
                # Log the actual data structure for debugging
                self.logger.debug(f"Case data structure: {list(case_data.keys())}")
                raise FirestoreServiceError(f"Failed to parse business case data: {str(parse_error)}")
            
        except FirestoreServiceError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving business case {case_id}: {str(e)}")
            raise FirestoreServiceError(f"Failed to retrieve business case: {str(e)}")

    async def update_business_case(self, case_id: str, updates: Dict[str, Any]) -> bool:
        """Update business case"""
        try:
            self.logger.info(f"Updating business case {case_id}")
            
            # Add updated timestamp
            updates['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            # Convert datetime objects to ISO strings if present
            for key, value in updates.items():
                if isinstance(value, datetime):
                    updates[key] = value.isoformat()
            
            case_ref = self._db.collection(self.business_cases_collection).document(case_id)
            
            # Check if case exists first
            doc = await asyncio.to_thread(case_ref.get)
            if not doc.exists:
                raise DocumentNotFoundError(f"Business case {case_id} not found")
            
            await asyncio.to_thread(case_ref.update, updates)
            
            self.logger.info(f"Business case {case_id} updated successfully")
            return True
            
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating business case {case_id}: {str(e)}")
            raise FirestoreServiceError(f"Failed to update business case: {str(e)}")

    async def list_business_cases_for_user(self, user_id: str, status_filter: Optional[str] = None) -> List[BusinessCaseData]:
        """List business cases for a specific user, optionally filtered by status"""
        try:
            self.logger.debug(f"Retrieving business cases for user {user_id}")
            
            cases_ref = self._db.collection(self.business_cases_collection)
            # Query by user_id field (used by BusinessCaseData) instead of request_data.requester_uid
            query = cases_ref.where("user_id", "==", user_id)
            
            if status_filter:
                query = query.where("status", "==", status_filter)
            
            docs = await asyncio.to_thread(query.stream)
            
            cases = []
            for doc in docs:
                if doc.exists:
                    case_data = doc.to_dict()
                    case_data['case_id'] = doc.id  # Ensure case_id is set
                    
                    # Convert ISO strings back to datetime objects if needed
                    if 'created_at' in case_data and isinstance(case_data['created_at'], str):
                        case_data['created_at'] = datetime.fromisoformat(case_data['created_at'])
                    if 'updated_at' in case_data and isinstance(case_data['updated_at'], str):
                        case_data['updated_at'] = datetime.fromisoformat(case_data['updated_at'])
                    
                    # Try to parse as BusinessCaseData
                    try:
                        cases.append(BusinessCaseData(**case_data))
                    except Exception as parse_error:
                        self.logger.warning(f"Failed to parse case {doc.id} as BusinessCaseData: {parse_error}")
                        continue  # Skip cases that can't be parsed
            
            self.logger.debug(f"Retrieved {len(cases)} business cases for user {user_id}")
            return cases
            
        except Exception as e:
            self.logger.error(f"Error listing business cases for user {user_id}: {str(e)}")
            raise FirestoreServiceError(f"Failed to list business cases for user: {str(e)}")

    async def get_business_cases_by_status(self, status: str) -> List[BusinessCase]:
        """Get all business cases with a specific status"""
        try:
            self.logger.debug(f"Retrieving business cases with status: {status}")
            
            cases_ref = self._db.collection(self.business_cases_collection)
            query = cases_ref.where("status", "==", status)
            docs = await asyncio.to_thread(query.stream)
            
            cases = []
            for doc in docs:
                if doc.exists:
                    case_data = doc.to_dict()
                    case_data['id'] = doc.id  # Ensure ID is set
                    
                    # Convert ISO strings back to datetime objects
                    if 'created_at' in case_data and isinstance(case_data['created_at'], str):
                        case_data['created_at'] = datetime.fromisoformat(case_data['created_at'])
                    if 'updated_at' in case_data and isinstance(case_data['updated_at'], str):
                        case_data['updated_at'] = datetime.fromisoformat(case_data['updated_at'])
                    if 'completed_at' in case_data and case_data['completed_at']:
                        case_data['completed_at'] = datetime.fromisoformat(case_data['completed_at'])
                    
                    # Handle nested datetime objects in request_data
                    if 'request_data' in case_data and 'deadline' in case_data['request_data']:
                        if case_data['request_data']['deadline']:
                            case_data['request_data']['deadline'] = datetime.fromisoformat(case_data['request_data']['deadline'])
                    
                    cases.append(BusinessCase(**case_data))
            
            self.logger.debug(f"Retrieved {len(cases)} business cases with status {status}")
            return cases
            
        except Exception as e:
            self.logger.error(f"Error retrieving business cases by status {status}: {str(e)}")
            raise FirestoreServiceError(f"Failed to retrieve business cases by status: {str(e)}")

    async def delete_business_case(self, case_id: str) -> bool:
        """Delete a business case"""
        try:
            self.logger.info(f"Deleting business case {case_id}")
            
            case_ref = self._db.collection(self.business_cases_collection).document(case_id)
            
            # Check if case exists first
            doc = await asyncio.to_thread(case_ref.get)
            if not doc.exists:
                raise DocumentNotFoundError(f"Business case {case_id} not found")
            
            await asyncio.to_thread(case_ref.delete)
            
            self.logger.info(f"Business case {case_id} deleted successfully")
            return True
            
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error deleting business case {case_id}: {str(e)}")
            raise FirestoreServiceError(f"Failed to delete business case: {str(e)}")

    # Job operations
    async def create_job(self, job: Job) -> Optional[str]:
        """Create a new job"""
        try:
            self.logger.info(f"Creating job: {job.job_type}")
            
            # Update timestamps
            job.created_at = datetime.now(timezone.utc)
            job.updated_at = datetime.now(timezone.utc)
            
            job_data = job.model_dump(exclude_none=True)
            
            # Convert datetime objects to ISO strings for Firestore
            if 'created_at' in job_data:
                job_data['created_at'] = job_data['created_at'].isoformat()
            if 'updated_at' in job_data:
                job_data['updated_at'] = job_data['updated_at'].isoformat()
            if 'started_at' in job_data and job_data['started_at']:
                job_data['started_at'] = job_data['started_at'].isoformat()
            if 'completed_at' in job_data and job_data['completed_at']:
                job_data['completed_at'] = job_data['completed_at'].isoformat()
            
            jobs_ref = self._db.collection(self.jobs_collection)
            
            if job.id:
                # Use specific ID if provided
                doc_ref = jobs_ref.document(job.id)
                await asyncio.to_thread(doc_ref.set, job_data)
                job_id = job.id
            else:
                # Auto-generate ID
                doc_ref = await asyncio.to_thread(jobs_ref.add, job_data)
                job_id = doc_ref[1].id
            
            self.logger.info(f"Job created with ID: {job_id}")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Error creating job: {str(e)}")
            raise FirestoreServiceError(f"Failed to create job: {str(e)}")

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        try:
            self.logger.debug(f"Retrieving job: {job_id}")
            
            job_ref = self._db.collection(self.jobs_collection).document(job_id)
            doc = await asyncio.to_thread(job_ref.get)
            
            if not doc.exists:
                self.logger.debug(f"Job {job_id} not found")
                return None
                
            job_data = doc.to_dict()
            job_data['id'] = job_id  # Ensure ID is set
            
            # Convert ISO strings back to datetime objects
            if 'created_at' in job_data and isinstance(job_data['created_at'], str):
                job_data['created_at'] = datetime.fromisoformat(job_data['created_at'])
            if 'updated_at' in job_data and isinstance(job_data['updated_at'], str):
                job_data['updated_at'] = datetime.fromisoformat(job_data['updated_at'])
            if 'started_at' in job_data and job_data['started_at']:
                job_data['started_at'] = datetime.fromisoformat(job_data['started_at'])
            if 'completed_at' in job_data and job_data['completed_at']:
                job_data['completed_at'] = datetime.fromisoformat(job_data['completed_at'])
            
            job = Job(**job_data)
            self.logger.debug(f"Job {job_id} retrieved successfully")
            return job
            
        except Exception as e:
            self.logger.error(f"Error retrieving job {job_id}: {str(e)}")
            raise FirestoreServiceError(f"Failed to retrieve job: {str(e)}")

    async def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update job status and information"""
        try:
            self.logger.info(f"Updating job {job_id}")
            
            # Add updated timestamp
            updates['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            # Convert datetime objects to ISO strings if present
            for key, value in updates.items():
                if isinstance(value, datetime):
                    updates[key] = value.isoformat()
            
            job_ref = self._db.collection(self.jobs_collection).document(job_id)
            
            # Check if job exists first
            doc = await asyncio.to_thread(job_ref.get)
            if not doc.exists:
                raise DocumentNotFoundError(f"Job {job_id} not found")
            
            await asyncio.to_thread(job_ref.update, updates)
            
            self.logger.info(f"Job {job_id} updated successfully")
            return True
            
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating job {job_id}: {str(e)}")
            raise FirestoreServiceError(f"Failed to update job: {str(e)}")

    async def list_jobs_for_user(self, user_id: str) -> List[Job]:
        """List jobs for a specific user"""
        try:
            self.logger.debug(f"Retrieving jobs for user {user_id}")
            
            jobs_ref = self._db.collection(self.jobs_collection)
            query = jobs_ref.where("user_uid", "==", user_id)
            docs = await asyncio.to_thread(query.stream)
            
            jobs = []
            for doc in docs:
                if doc.exists:
                    job_data = doc.to_dict()
                    job_data['id'] = doc.id  # Ensure ID is set
                    
                    # Convert ISO strings back to datetime objects
                    if 'created_at' in job_data and isinstance(job_data['created_at'], str):
                        job_data['created_at'] = datetime.fromisoformat(job_data['created_at'])
                    if 'updated_at' in job_data and isinstance(job_data['updated_at'], str):
                        job_data['updated_at'] = datetime.fromisoformat(job_data['updated_at'])
                    if 'started_at' in job_data and job_data['started_at']:
                        job_data['started_at'] = datetime.fromisoformat(job_data['started_at'])
                    if 'completed_at' in job_data and job_data['completed_at']:
                        job_data['completed_at'] = datetime.fromisoformat(job_data['completed_at'])
                    
                    jobs.append(Job(**job_data))
            
            self.logger.debug(f"Retrieved {len(jobs)} jobs for user {user_id}")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error listing jobs for user {user_id}: {str(e)}")
            raise FirestoreServiceError(f"Failed to list jobs for user: {str(e)}")

    async def list_jobs_by_status(self, status: JobStatus) -> List[Job]:
        """List jobs by status"""
        try:
            self.logger.debug(f"Retrieving jobs with status: {status.value}")
            
            jobs_ref = self._db.collection(self.jobs_collection)
            query = jobs_ref.where("status", "==", status.value)
            docs = await asyncio.to_thread(query.stream)
            
            jobs = []
            for doc in docs:
                if doc.exists:
                    job_data = doc.to_dict()
                    job_data['id'] = doc.id  # Ensure ID is set
                    
                    # Convert ISO strings back to datetime objects
                    if 'created_at' in job_data and isinstance(job_data['created_at'], str):
                        job_data['created_at'] = datetime.fromisoformat(job_data['created_at'])
                    if 'updated_at' in job_data and isinstance(job_data['updated_at'], str):
                        job_data['updated_at'] = datetime.fromisoformat(job_data['updated_at'])
                    if 'started_at' in job_data and job_data['started_at']:
                        job_data['started_at'] = datetime.fromisoformat(job_data['started_at'])
                    if 'completed_at' in job_data and job_data['completed_at']:
                        job_data['completed_at'] = datetime.fromisoformat(job_data['completed_at'])
                    
                    jobs.append(Job(**job_data))
            
            self.logger.debug(f"Retrieved {len(jobs)} jobs with status {status.value}")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error listing jobs by status {status.value}: {str(e)}")
            raise FirestoreServiceError(f"Failed to list jobs by status: {str(e)}")

    async def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        try:
            self.logger.info(f"Deleting job {job_id}")
            
            job_ref = self._db.collection(self.jobs_collection).document(job_id)
            
            # Check if job exists first
            doc = await asyncio.to_thread(job_ref.get)
            if not doc.exists:
                raise DocumentNotFoundError(f"Job {job_id} not found")
            
            await asyncio.to_thread(job_ref.delete)
            
            self.logger.info(f"Job {job_id} deleted successfully")
            return True
            
        except DocumentNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error deleting job {job_id}: {str(e)}")
            raise FirestoreServiceError(f"Failed to delete job: {str(e)}")


# Global Firestore service instance
firestore_service = FirestoreService()
