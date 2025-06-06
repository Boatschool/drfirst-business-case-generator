"""
Unit tests for PRD update functionality.
Tests the PrdUpdateRequest model and related validation logic.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from app.api.v1.cases.models import PrdUpdateRequest


class TestPrdUpdateRequest:
    """Test the PrdUpdateRequest Pydantic model."""

    def test_valid_prd_update_request(self):
        """Test creating a valid PRD update request."""
        content = "# Updated PRD\n\nThis is a test PRD content."
        request = PrdUpdateRequest(content_markdown=content)

        assert request.content_markdown == content
        assert isinstance(request.content_markdown, str)

    def test_prd_update_request_with_empty_content(self):
        """Test that empty content is allowed (user might want to clear PRD)."""
        request = PrdUpdateRequest(content_markdown="")
        assert request.content_markdown == ""

    def test_prd_update_request_with_long_content(self):
        """Test that long content is handled properly."""
        long_content = "# Long PRD\n\n" + "This is a very long line. " * 1000
        request = PrdUpdateRequest(content_markdown=long_content)
        assert len(request.content_markdown) > 10000
        assert request.content_markdown.startswith("# Long PRD")

    def test_prd_update_request_with_markdown_formatting(self):
        """Test that markdown formatting is preserved."""
        markdown_content = """# PRD Title

## Overview
This is a **bold** text and *italic* text.

### Features
- Feature 1
- Feature 2
  - Sub-feature 2.1
  - Sub-feature 2.2

```python
def example_code():
    return "Hello World"
```

[Link to documentation](https://example.com)

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
"""
        request = PrdUpdateRequest(content_markdown=markdown_content)
        assert "**bold**" in request.content_markdown
        assert "*italic*" in request.content_markdown
        assert "```python" in request.content_markdown
        assert "[Link to documentation]" in request.content_markdown

    def test_prd_update_request_missing_content_markdown(self):
        """Test that missing content_markdown raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PrdUpdateRequest()

        error = exc_info.value
        assert "content_markdown" in str(error)
        assert "Field required" in str(error)

    def test_prd_update_request_invalid_type(self):
        """Test that non-string content_markdown raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PrdUpdateRequest(content_markdown=123)

        error = exc_info.value
        assert "content_markdown" in str(error)
        assert "str_type" in str(error) or "string" in str(error)

    def test_prd_update_request_none_content(self):
        """Test that None content raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PrdUpdateRequest(content_markdown=None)

        error = exc_info.value
        assert "content_markdown" in str(error)

    def test_prd_update_request_serialization(self):
        """Test that the model can be serialized to JSON."""
        content = "# Test PRD\n\nContent with unicode: 🚀"
        request = PrdUpdateRequest(content_markdown=content)

        # Test model_dump
        data = request.model_dump()
        assert data == {"content_markdown": content}

        # Test JSON serialization
        json_str = request.model_dump_json()
        assert "Test PRD" in json_str
        assert "🚀" in json_str

    def test_prd_update_request_deserialization(self):
        """Test that the model can be created from dictionary."""
        data = {"content_markdown": "# Deserialized PRD\n\nTest content"}
        request = PrdUpdateRequest(**data)
        assert request.content_markdown == data["content_markdown"]

    def test_prd_update_request_with_special_characters(self):
        """Test handling of special characters and encoding."""
        special_content = """# PRD with Special Characters

## Unicode Support
- Emoji: 🚀 🎯 ✅ 🔧
- Accents: café, naïve, résumé
- Symbols: ©, ®, ™, €, £, ¥
- Math: ∑, ∆, π, α, β, γ

## Code Examples
```javascript
const message = "Hello, 世界!";
console.log(message);
```
"""
        request = PrdUpdateRequest(content_markdown=special_content)
        assert "🚀" in request.content_markdown
        assert "café" in request.content_markdown
        assert "世界" in request.content_markdown

    def test_prd_update_request_field_validation(self):
        """Test field validation edge cases."""
        # Test with whitespace-only content
        request = PrdUpdateRequest(content_markdown="   \n\t   ")
        assert request.content_markdown == "   \n\t   "

        # Test with newlines
        request = PrdUpdateRequest(content_markdown="\n\n\n")
        assert request.content_markdown == "\n\n\n"
