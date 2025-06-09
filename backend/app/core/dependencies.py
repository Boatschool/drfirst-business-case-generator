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


def reset_all_singletons():
    """
    Reset all singleton instances. Useful for reloads.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("🔄 Resetting all singletons...")
    
    # Reset database client
    reset_db()
    logger.info("  - Database client reset")
    
    # Reset auth service
    try:
        from app.services.auth_service import get_auth_service
        auth_service = get_auth_service()
        auth_service.reset()
        logger.info("  - AuthService reset")
    except ImportError:
        logger.warning("  - AuthService not found for reset")
        
    # Reset vertex AI service
    try:
        from app.services.vertex_ai_service import vertex_ai_service
        vertex_ai_service.reset()
        logger.info("  - VertexAIService reset")
    except ImportError:
        logger.warning("  - VertexAIService not found for reset")


def cleanup_all_singletons():
    """
    Cleanup all singleton instances with proper resource management.
    
    This function performs comprehensive cleanup of all singleton services
    to prevent resource leaks during application shutdown or reloads.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("🧹 Cleaning up all singletons...")
    
    # Cleanup database client (Firestore)
    try:
        from app.core.firestore_impl import FirestoreClient
        FirestoreClient.reset_singleton()
        logger.info("  - ✅ Firestore client cleaned up")
    except ImportError:
        logger.warning("  - ⚠️ Firestore client not found for cleanup")
    except Exception as e:
        logger.error(f"  - ❌ Error cleaning up Firestore: {e}")
    
    # Cleanup auth service (Firebase Admin)
    try:
        from app.services.auth_service import get_auth_service
        auth_service = get_auth_service()
        auth_service.cleanup()
        logger.info("  - ✅ AuthService cleaned up")
    except ImportError:
        logger.warning("  - ⚠️ AuthService not found for cleanup")
    except Exception as e:
        logger.error(f"  - ❌ Error cleaning up AuthService: {e}")
        
    # Cleanup vertex AI service
    try:
        from app.services.vertex_ai_service import vertex_ai_service
        vertex_ai_service.cleanup()
        logger.info("  - ✅ VertexAIService cleaned up")
    except ImportError:
        logger.warning("  - ⚠️ VertexAIService not found for cleanup")
    except Exception as e:
        logger.error(f"  - ❌ Error cleaning up VertexAIService: {e}")
    
    # Reset database client singleton after cleanup
    reset_db()
    logger.info("  - ✅ Database client singleton reset")
    
    logger.info("🎉 All singleton cleanup completed")


# FirestoreService dependency injection
def get_firestore_service():
    """
    Get FirestoreService instance with database dependency injection.
    
    Returns:
        FirestoreService: Service instance with injected database client
    """
    from app.services.firestore_service import FirestoreService
    return FirestoreService(db=get_db()) 