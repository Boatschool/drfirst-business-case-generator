"""
Firestore implementation of the database interface.
"""

import os
from typing import Any, Dict, List, Optional, Union

from app.core.database import (
    DatabaseClient, CollectionReference, DocumentReference, 
    DocumentSnapshot, Query, ArrayUnion, Increment
)


class FirestoreClient(DatabaseClient):
    """Firestore implementation of DatabaseClient."""
    
    def __init__(self, project_id: Optional[str] = None):
        # Only import when actually needed (lazy loading)
        from google.cloud import firestore
        
        self._client = firestore.Client(project=project_id)
        self._firestore = firestore  # Keep reference for operations
    
    def collection(self, name: str) -> "FirestoreCollectionReference":
        """Get a collection reference."""
        return FirestoreCollectionReference(
            self._client.collection(name), 
            self._firestore
        )


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