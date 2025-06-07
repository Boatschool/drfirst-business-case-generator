"""
Firestore implementation of the database interface.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from app.core.database import (
    DatabaseClient, CollectionReference, DocumentReference, 
    DocumentSnapshot, Query, ArrayUnion, Increment
)

logger = logging.getLogger(__name__)


class FirestoreClient(DatabaseClient):
    """Firestore implementation of DatabaseClient with proper resource management."""

    _instance = None
    _initialized = False

    def __new__(cls, project_id: Optional[str] = None):
        """Implement singleton pattern to prevent multiple client instances."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, project_id: Optional[str] = None):
        # Prevent re-initialization of the same instance
        if self._initialized:
            return
            
        # Only import when actually needed (lazy loading)
        from google.cloud import firestore

        self._client = firestore.Client(project=project_id)
        self._firestore = firestore  # Keep reference for operations
        self._project_id = project_id
        self._initialized = True
        
        logger.info(f"🔥 Firestore client initialized for project: {project_id}")

    def collection(self, name: str) -> "FirestoreCollectionReference":
        """Get a collection reference."""
        return FirestoreCollectionReference(
            self._client.collection(name), 
            self._firestore
        )

    def cleanup(self) -> None:
        """
        Cleanup Firestore client resources to prevent connection leaks.
        
        This method should be called during application shutdown to properly
        close connections and prevent resource accumulation.
        """
        try:
            if hasattr(self, '_client') and self._client:
                # Close the Firestore client if it has a close method
                if hasattr(self._client, 'close'):
                    self._client.close()
                    logger.info("🧹 Firestore client connection closed successfully")
                else:
                    # For Firestore clients that don't have explicit close methods,
                    # we reset the instance to allow garbage collection
                    logger.info("🧹 Firestore client marked for garbage collection")
                
                # Clear the client reference
                self._client = None
                
        except Exception as e:
            logger.error(f"❌ Error closing Firestore client: {e}")
        finally:
            self._initialized = False
            logger.info("🔄 Firestore client cleanup completed")

    def reset(self) -> None:
        """
        Reset client state for clean reloads.
        
        This method resets the initialization state without closing connections,
        useful for development reloads where we want to reinitialize.
        """
        logger.info("🔄 Resetting Firestore client state for reload")
        self._initialized = False
        
    @classmethod
    def reset_singleton(cls) -> None:
        """
        Reset singleton instance for clean reloads.
        
        This class method allows external code to reset the singleton,
        which is useful during application lifecycle management.
        """
        if cls._instance is not None:
            # Cleanup existing instance
            cls._instance.cleanup()
            # Reset class-level state
            cls._instance = None
            cls._initialized = False
            logger.info("🔄 Firestore singleton reset completed")

    def get_status(self) -> Dict[str, Any]:
        """
        Get status information about the Firestore client.
        
        Returns:
            dict: Status information including connection health
        """
        status = {
            "initialized": self._initialized,
            "client_available": hasattr(self, '_client') and self._client is not None,
            "project_id": getattr(self, '_project_id', None),
            "service_name": "Firestore Client"
        }
        
        # Test connection health
        try:
            if self._initialized and hasattr(self, '_client') and self._client:
                # Simple test to verify connection
                collections = list(self._client.collections())
                status["connection_healthy"] = True
                status["collections_accessible"] = True
            else:
                status["connection_healthy"] = False
                status["collections_accessible"] = False
        except Exception as e:
            status["connection_healthy"] = False
            status["connection_error"] = str(e)
            status["collections_accessible"] = False
        
        return status


class FirestoreCollectionReference(CollectionReference):
    """Firestore implementation of CollectionReference."""

    def __init__(self, collection_ref, firestore_module):
        self._collection_ref = collection_ref
        self._firestore = firestore_module

    def document(self, doc_id: str) -> "FirestoreDocumentReference":
        """Get a document reference."""
        return FirestoreDocumentReference(
            self._collection_ref.document(doc_id),
            self._firestore
        )

    def add(self, data: Dict[str, Any]) -> "FirestoreDocumentReference":
        """Add a new document."""
        doc_ref = self._collection_ref.add(data)[1]
        return FirestoreDocumentReference(doc_ref, self._firestore)

    def stream(self) -> List["FirestoreDocumentSnapshot"]:
        """Stream all documents in the collection."""
        docs = self._collection_ref.stream()
        return [FirestoreDocumentSnapshot(doc) for doc in docs]

    def where(self, field: str, op: str, value: Any) -> "FirestoreQuery":
        """Create a query with a where clause."""
        query = self._collection_ref.where(field, op, value)
        return FirestoreQuery(query)

    def order_by(self, field: str, direction: str = "ASCENDING") -> "FirestoreQuery":
        """Create a query with ordering."""
        direction_enum = getattr(self._firestore.Query, direction)
        query = self._collection_ref.order_by(field, direction=direction_enum)
        return FirestoreQuery(query)


class FirestoreDocumentReference(DocumentReference):
    """Firestore implementation of DocumentReference."""

    def __init__(self, doc_ref, firestore_module):
        self._doc_ref = doc_ref
        self._firestore = firestore_module

    def get(self) -> "FirestoreDocumentSnapshot":
        """Get the document."""
        doc = self._doc_ref.get()
        return FirestoreDocumentSnapshot(doc)

    def set(self, data: Dict[str, Any], merge: bool = False) -> None:
        """Set document data."""
        # Convert our abstract operations to Firestore operations
        converted_data = self._convert_operations(data)
        self._doc_ref.set(converted_data, merge=merge)

    def update(self, data: Dict[str, Any]) -> None:
        """Update document data."""
        # Convert our abstract operations to Firestore operations
        converted_data = self._convert_operations(data)
        self._doc_ref.update(converted_data)

    def delete(self) -> None:
        """Delete the document."""
        self._doc_ref.delete()

    def _convert_operations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert abstract operations to Firestore operations."""
        converted = {}
        for key, value in data.items():
            if isinstance(value, ArrayUnion):
                converted[key] = self._firestore.ArrayUnion(value.values)
            elif isinstance(value, Increment):
                converted[key] = self._firestore.Increment(value.value)
            else:
                converted[key] = value
        return converted


class FirestoreDocumentSnapshot(DocumentSnapshot):
    """Firestore implementation of DocumentSnapshot."""

    def __init__(self, doc_snapshot):
        self._doc_snapshot = doc_snapshot

    @property
    def exists(self) -> bool:
        """Check if document exists."""
        return self._doc_snapshot.exists

    @property
    def id(self) -> str:
        """Get document ID."""
        return self._doc_snapshot.id

    def to_dict(self) -> Optional[Dict[str, Any]]:
        """Convert to dictionary."""
        return self._doc_snapshot.to_dict()


class FirestoreQuery(Query):
    """Firestore implementation of Query."""

    def __init__(self, query):
        self._query = query

    def where(self, field: str, op: str, value: Any) -> "FirestoreQuery":
        """Add a where clause."""
        new_query = self._query.where(field, op, value)
        return FirestoreQuery(new_query)

    def order_by(self, field: str, direction: str = "ASCENDING") -> "FirestoreQuery":
        """Add ordering."""
        from google.cloud import firestore
        direction_enum = getattr(firestore.Query, direction)
        new_query = self._query.order_by(field, direction=direction_enum)
        return FirestoreQuery(new_query)

    def limit(self, count: int) -> "FirestoreQuery":
        """Limit results."""
        new_query = self._query.limit(count)
        return FirestoreQuery(new_query)

    def stream(self) -> List[FirestoreDocumentSnapshot]:
        """Execute query and return results."""
        docs = self._query.stream()
        return [FirestoreDocumentSnapshot(doc) for doc in docs] 
