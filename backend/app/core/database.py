"""
Database abstraction layer for dependency injection.
Provides interfaces and implementations for data access.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class DatabaseClient(ABC):
    """Abstract interface for database operations."""
    
    @abstractmethod
    def collection(self, name: str) -> "CollectionReference":
        """Get a collection reference."""
        pass


class CollectionReference(ABC):
    """Abstract interface for collection operations."""
    
    @abstractmethod
    def document(self, doc_id: str) -> "DocumentReference":
        """Get a document reference."""
        pass
    
    @abstractmethod
    def add(self, data: Dict[str, Any]) -> "DocumentReference":
        """Add a new document."""
        pass
    
    @abstractmethod
    def stream(self) -> List["DocumentSnapshot"]:
        """Stream all documents in the collection."""
        pass
    
    @abstractmethod
    def where(self, field: str, op: str, value: Any) -> "Query":
        """Create a query with a where clause."""
        pass
    
    @abstractmethod
    def order_by(self, field: str, direction: str = "ASCENDING") -> "Query":
        """Create a query with ordering."""
        pass


class DocumentReference(ABC):
    """Abstract interface for document operations."""
    
    @abstractmethod
    def get(self) -> "DocumentSnapshot":
        """Get the document."""
        pass
    
    @abstractmethod
    def set(self, data: Dict[str, Any], merge: bool = False) -> None:
        """Set document data."""
        pass
    
    @abstractmethod
    def update(self, data: Dict[str, Any]) -> None:
        """Update document data."""
        pass
    
    @abstractmethod
    def delete(self) -> None:
        """Delete the document."""
        pass


class DocumentSnapshot(ABC):
    """Abstract interface for document snapshot."""
    
    @property
    @abstractmethod
    def exists(self) -> bool:
        """Check if document exists."""
        pass
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Get document ID."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Optional[Dict[str, Any]]:
        """Convert to dictionary."""
        pass


class Query(ABC):
    """Abstract interface for queries."""
    
    @abstractmethod
    def where(self, field: str, op: str, value: Any) -> "Query":
        """Add a where clause."""
        pass
    
    @abstractmethod
    def order_by(self, field: str, direction: str = "ASCENDING") -> "Query":
        """Add ordering."""
        pass
    
    @abstractmethod
    def limit(self, count: int) -> "Query":
        """Limit results."""
        pass
    
    @abstractmethod
    def stream(self) -> List[DocumentSnapshot]:
        """Execute query and return results."""
        pass


class ArrayUnion:
    """Abstract array union operation."""
    
    def __init__(self, values: List[Any]):
        self.values = values


class Increment:
    """Abstract increment operation."""
    
    def __init__(self, value: Union[int, float]):
        self.value = value 