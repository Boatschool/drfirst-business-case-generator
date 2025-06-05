"""
Dependency injection container for managing database implementations.
"""

import os
from typing import Optional

from app.core.database import DatabaseClient, ArrayUnion, Increment
from app.core.config import settings


def get_database_client() -> DatabaseClient:
    """
    Factory function to get the appropriate database client based on environment.
    
    Returns:
        DatabaseClient: Either FirestoreClient for production or MockClient for testing
    """
    environment = os.getenv('ENVIRONMENT', getattr(settings, 'environment', 'development'))
    
    if environment == 'test':
        from app.core.mock_impl import MockClient
        return MockClient(project_id=settings.firebase_project_id)
    else:
        from app.core.firestore_impl import FirestoreClient
        return FirestoreClient(project_id=settings.firebase_project_id)


def get_array_union(values: list) -> ArrayUnion:
    """
    Factory function to create ArrayUnion operations.
    
    Args:
        values: List of values to union with existing array
        
    Returns:
        ArrayUnion: Abstract array union operation
    """
    return ArrayUnion(values)


def get_increment(value: int) -> Increment:
    """
    Factory function to create Increment operations.
    
    Args:
        value: Value to increment by
        
    Returns:
        Increment: Abstract increment operation
    """
    return Increment(value)


# Singleton instance for dependency injection
_db_client: Optional[DatabaseClient] = None


def get_db() -> DatabaseClient:
    """
    Get singleton database client instance.
    
    Returns:
        DatabaseClient: The database client instance
    """
    global _db_client
    if _db_client is None:
        _db_client = get_database_client()
    return _db_client


def reset_db():
    """
    Reset the database client singleton. Useful for testing.
    """
    global _db_client
    _db_client = None 