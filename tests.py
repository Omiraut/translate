"""
Integration tests for Translation API
Run with: pytest tests.py -v
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"


class TestLanguagesEndpoint:
    """Test languages listing endpoint"""

    def test_get_languages(self):
        """Test /languages endpoint"""
        response = client.get("/languages")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True
        assert data["code"] == 200
        assert isinstance(data["data"], dict)
        assert "hi" in data["data"]
        assert "mr" in data["data"]

    def test_supported_languages_count(self):
        """Verify minimum supported languages"""
        response = client.get("/languages")
        data = response.json()
        # Should have at least 8 Indian languages
        assert len(data["data"]) >= 8


class TestTranslationEndpoint:
    """Test translation endpoint"""

    def test_translate_valid_request(self):
        """Test translation with valid input"""
        response = client.post(
            "/translate",
            json={"message": "Hello", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True
        assert data["code"] == 200
        assert "converted_text" in data["data"]
        assert data["data"]["language"] == "hi"

    def test_translate_empty_message(self):
        """Test translation with empty message"""
        response = client.post(
            "/translate",
            json={"message": "", "language": "hi"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == False
        assert "empty" in data["message"].lower()

    def test_translate_invalid_language(self):
        """Test translation with invalid language"""
        response = client.post(
            "/translate",
            json={"message": "Hello", "language": "xyz"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == False
        assert "unsupported" in data["message"].lower()

    def test_translate_whitespace_message(self):
        """Test translation with whitespace-only message"""
        response = client.post(
            "/translate",
            json={"message": "   ", "language": "hi"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == False

    def test_translate_caching(self):
        """Test that caching works (same request returns cached result)"""
        # First request
        response1 = client.post(
            "/translate",
            json={"message": "Test", "language": "hi"},
        )
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request (should be cached)
        response2 = client.post(
            "/translate",
            json={"message": "Test", "language": "hi"},
        )
        assert response2.status_code == 200
        data2 = response2.json()

        # Both should have same translation
        assert data1["data"]["converted_text"] == data2["data"]["converted_text"]
        assert data2["data"]["cached"] == True

    def test_translate_multiple_languages(self):
        """Test translation to multiple languages"""
        test_cases = [
            ("Hi", "hi", "हिंदी"),  # Hindi
            ("Hello", "mr", "मराठी"),  # Marathi
            ("Hi", "bn", "বাংলা"),  # Bengali
        ]

        for message, language, language_name in test_cases:
            response = client.post(
                "/translate",
                json={"message": message, "language": language},
            )
            assert response.status_code == 200, f"Failed for {language_name}"
            data = response.json()
            assert data["status"] == True
            assert "converted_text" in data["data"]


class TestStatsEndpoint:
    """Test statistics endpoint"""

    def test_get_stats(self):
        """Test /stats endpoint"""
        # Make at least one translation first
        client.post(
            "/translate",
            json={"message": "Hello", "language": "hi"},
        )

        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True
        assert data["code"] == 200
        assert "total_translations" in data["data"]
        assert "cache_stats" in data["data"]


class TestCacheManagement:
    """Test cache management endpoints"""

    def test_clear_cache(self):
        """Test /cache/clear endpoint"""
        # Make a translation to populate cache
        client.post(
            "/translate",
            json={"message": "Hello", "language": "hi"},
        )

        # Clear cache
        response = client.post("/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True
        assert "cleared" in data["message"].lower()


class TestErrorHandling:
    """Test error handling"""

    def test_missing_required_fields(self):
        """Test request with missing required fields"""
        # Missing language
        response = client.post(
            "/translate",
            json={"message": "Hello"},
        )
        assert response.status_code == 422  # Validation error

        # Missing message
        response = client.post(
            "/translate",
            json={"language": "hi"},
        )
        assert response.status_code == 422

    def test_message_too_long(self):
        """Test message that exceeds max length"""
        long_message = "x" * 10001
        response = client.post(
            "/translate",
            json={"message": long_message, "language": "hi"},
        )
        assert response.status_code == 400

    def test_language_case_insensitive(self):
        """Test that language codes are case-insensitive"""
        response = client.post(
            "/translate",
            json={"message": "Hello", "language": "HI"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
