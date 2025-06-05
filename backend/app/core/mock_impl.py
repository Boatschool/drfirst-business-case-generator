"""
Mock implementation of the database interface for testing.
"""

import copy
from typing import Any, Dict, List, Optional, Union

from app.core.database import (
    DatabaseClient, CollectionReference, DocumentReference, 
    DocumentSnapshot, Query, ArrayUnion, Increment
)


class MockClient(DatabaseClient):
    """Mock implementation of DatabaseClient for testing."""
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id
        self._data: Dict[str, Dict[str, Dict[str, Any]]] = {}
    
    def collection(self, name: str) -> "MockCollectionReference":
        """Get a collection reference."""
        if name not in self._data:
            self._data[name] = {}
        return MockCollectionReference(name, self._data[name], self._data)


class MockCollectionReference(CollectionReference):
    """Mock implementation of CollectionReference."""
    
    def __init__(self, name: str, collection_data: Dict[str, Dict[str, Any]], all_data: Dict):
        self.name = name
        self._collection_data = collection_data
        self._all_data = all_data
    
    def document(self, doc_id: str) -> "MockDocumentReference":
        """Get a document reference."""
        return MockDocumentReference(
            doc_id, 
            self._collection_data, 
            self.name
        )
    
    def add(self, data: Dict[str, Any]) -> "MockDocumentReference":
        """Add a new document."""
        import uuid
        doc_id = str(uuid.uuid4())
        doc_ref = self.document(doc_id)
        doc_ref.set(data)
        return doc_ref
    
    def stream(self) -> List["MockDocumentSnapshot"]:
        """Stream all documents in the collection."""
        snapshots = []
        for doc_id, doc_data in self._collection_data.items():
            snapshot = MockDocumentSnapshot(doc_id, doc_data, exists=True)
            snapshots.append(snapshot)
        return snapshots
    
    def where(self, field: str, op: str, value: Any) -> "MockQuery":
        """Create a query with a where clause."""
        return MockQuery(self._collection_data).where(field, op, value)
    
    def order_by(self, field: str, direction: str = "ASCENDING") -> "MockQuery":
        """Create a query with ordering."""
        return MockQuery(self._collection_data).order_by(field, direction)


class MockDocumentReference(DocumentReference):
    """Mock implementation of DocumentReference."""
    
    def __init__(self, doc_id: str, collection_data: Dict[str, Dict[str, Any]], collection_name: str):
        self.id = doc_id
        self._collection_data = collection_data
        self._collection_name = collection_name
    
    def get(self) -> "MockDocumentSnapshot":
        """Get the document."""
        doc_data = self._collection_data.get(self.id)
        exists = doc_data is not None
        return MockDocumentSnapshot(self.id, doc_data, exists)
    
    def set(self, data: Dict[str, Any], merge: bool = False) -> None:
        """Set document data."""
        processed_data = self._process_operations(data)
        
        if merge and self.id in self._collection_data:
            # Merge with existing data
            existing_data = copy.deepcopy(self._collection_data[self.id])
            existing_data.update(processed_data)
            self._collection_data[self.id] = existing_data
        else:
            # Replace entirely
            self._collection_data[self.id] = copy.deepcopy(processed_data)
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update document data."""
        if self.id not in self._collection_data:
            raise Exception(f"Document {self.id} does not exist")
        
        processed_data = self._process_operations(data)
        existing_data = copy.deepcopy(self._collection_data[self.id])
        existing_data.update(processed_data)
        self._collection_data[self.id] = existing_data
    
    def delete(self) -> None:
        """Delete the document."""
        if self.id in self._collection_data:
            del self._collection_data[self.id]
    
    def _process_operations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process abstract operations into actual data changes."""
        processed = {}
        
        for key, value in data.items():
            if isinstance(value, ArrayUnion):
                # Simulate ArrayUnion by appending to existing array
                existing_data = self._collection_data.get(self.id, {})
                existing_array = existing_data.get(key, [])
                
                # Add new values that aren't already in the array
                for new_value in value.values:
                    if new_value not in existing_array:
                        existing_array.append(new_value)
                
                processed[key] = existing_array
            
            elif isinstance(value, Increment):
                # Simulate Increment by adding to existing value
                existing_data = self._collection_data.get(self.id, {})
                existing_value = existing_data.get(key, 0)
                processed[key] = existing_value + value.value
            
            else:
                processed[key] = value
        
        return processed


class MockDocumentSnapshot(DocumentSnapshot):
    """Mock implementation of DocumentSnapshot."""
    
    def __init__(self, doc_id: str, doc_data: Optional[Dict[str, Any]], exists: bool):
        self._id = doc_id
        self._data = doc_data
        self._exists = exists
    
    @property
    def exists(self) -> bool:
        """Check if document exists."""
        return self._exists
    
    @property
    def id(self) -> str:
        """Get document ID."""
        return self._id
    
    def to_dict(self) -> Optional[Dict[str, Any]]:
        """Convert to dictionary."""
        return copy.deepcopy(self._data) if self._data else None


class MockQuery(Query):
    """Mock implementation of Query."""
    
    def __init__(self, collection_data: Dict[str, Dict[str, Any]]):
        self._collection_data = collection_data
        self._filters: List[Dict[str, Any]] = []
        self._ordering: Optional[Dict[str, str]] = None
        self._limit_count: Optional[int] = None
    
    def where(self, field: str, op: str, value: Any) -> "MockQuery":
        """Add a where clause."""
        new_query = MockQuery(self._collection_data)
        new_query._filters = self._filters + [{"field": field, "op": op, "value": value}]
        new_query._ordering = self._ordering
        new_query._limit_count = self._limit_count
        return new_query
    
    def order_by(self, field: str, direction: str = "ASCENDING") -> "MockQuery":
        """Add ordering."""
        new_query = MockQuery(self._collection_data)
        new_query._filters = self._filters
        new_query._ordering = {"field": field, "direction": direction}
        new_query._limit_count = self._limit_count
        return new_query
    
    def limit(self, count: int) -> "MockQuery":
        """Limit results."""
        new_query = MockQuery(self._collection_data)
        new_query._filters = self._filters
        new_query._ordering = self._ordering
        new_query._limit_count = count
        return new_query
    
    def stream(self) -> List[MockDocumentSnapshot]:
        """Execute query and return results."""
        # Start with all documents
        results = []
        for doc_id, doc_data in self._collection_data.items():
            snapshot = MockDocumentSnapshot(doc_id, doc_data, True)
            results.append(snapshot)
        
        # Apply filters
        for filter_condition in self._filters:
            results = self._apply_filter(results, filter_condition)
        
        # Apply ordering
        if self._ordering:
            results = self._apply_ordering(results, self._ordering)
        
        # Apply limit
        if self._limit_count:
            results = results[:self._limit_count]
        
        return results
    
    def _apply_filter(self, docs: List[MockDocumentSnapshot], filter_condition: Dict[str, Any]) -> List[MockDocumentSnapshot]:
        """Apply a filter condition to documents."""
        field = filter_condition["field"]
        op = filter_condition["op"]
        value = filter_condition["value"]
        
        filtered = []
        for doc in docs:
            doc_data = doc.to_dict()
            if not doc_data:
                continue
            
            doc_value = self._get_nested_value(doc_data, field)
            
            if self._matches_condition(doc_value, op, value):
                filtered.append(doc)
        
        return filtered
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested field path (e.g., 'user.name')."""
        keys = field_path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _matches_condition(self, doc_value: Any, op: str, target_value: Any) -> bool:
        """Check if document value matches the filter condition."""
        if op == "==":
            return doc_value == target_value
        elif op == "!=":
            return doc_value != target_value
        elif op == "<":
            return doc_value < target_value
        elif op == "<=":
            return doc_value <= target_value
        elif op == ">":
            return doc_value > target_value
        elif op == ">=":
            return doc_value >= target_value
        elif op == "in":
            return doc_value in target_value
        elif op == "not-in":
            return doc_value not in target_value
        elif op == "array-contains":
            return isinstance(doc_value, list) and target_value in doc_value
        else:
            return False
    
    def _apply_ordering(self, docs: List[MockDocumentSnapshot], ordering: Dict[str, str]) -> List[MockDocumentSnapshot]:
        """Apply ordering to documents."""
        field = ordering["field"]
        direction = ordering["direction"]
        
        def sort_key(doc: MockDocumentSnapshot):
            doc_data = doc.to_dict()
            if not doc_data:
                return None
            return self._get_nested_value(doc_data, field)
        
        reverse = direction.upper() == "DESCENDING"
        return sorted(docs, key=sort_key, reverse=reverse) 