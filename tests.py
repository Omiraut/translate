"""
Comprehensive integration tests for Translation API
Run with: pytest tests.py -v --cov=. --cov-report=html
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

    def test_health_check_response_structure(self):
        """Verify health check response structure"""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data


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

    def test_languages_response_structure(self):
        """Verify languages response contains required fields"""
        response = client.get("/languages")
        data = response.json()
        assert "status" in data
        assert "code" in data
        assert "data" in data
        for lang_code in data["data"]:
            assert isinstance(lang_code, str)


class TestBasicTranslation:
    """Test basic translation functionality"""

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
        assert len(data["data"]["converted_text"]) > 0

    def test_translate_response_structure(self):
        """Verify translation response structure"""
        response = client.post(
            "/translate",
            json={"message": "Test", "language": "mr"},
        )
        data = response.json()
        assert "status" in data
        assert "code" in data
        assert "message" in data
        assert "data" in data
        assert "converted_text" in data["data"]
        assert "language" in data["data"]
        assert "cached" in data["data"]

    def test_translate_to_various_languages(self):
        """Test translation to multiple languages"""
        test_cases = [
            ("Hi", "hi"),  # Hindi
            ("Hello", "mr"),  # Marathi
            ("Hi", "bn"),  # Bengali
            ("Welcome", "gu"),  # Gujarati
            ("Hi", "ta"),  # Tamil
        ]

        for message, language in test_cases:
            response = client.post(
                "/translate",
                json={"message": message, "language": language},
            )
            assert response.status_code == 200, f"Failed for {language}"
            data = response.json()
            assert data["status"] == True
            assert "converted_text" in data["data"]

    def test_translate_case_insensitive_language(self):
        """Test that language codes are case-insensitive"""
        response = client.post(
            "/translate",
            json={"message": "Hello", "language": "HI"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True

    def test_translate_special_characters(self):
        """Test translation with special characters"""
        response = client.post(
            "/translate",
            json={"message": "Hello! How are you?", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True

    def test_translate_numbers(self):
        """Test translation with numbers"""
        response = client.post(
            "/translate",
            json={"message": "Number 123", "language": "mr"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True


class TestSemicolonSeparatedTranslations:
    """Test semicolon-separated batch translation feature"""

    def test_semicolon_separated_messages(self):
        """Test translation with semicolon-separated messages"""
        response = client.post(
            "/translate",
            json={"message": "Hello;Good morning;Welcome", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True
        assert "converted_text" in data["data"]
        
        # Check that converted_text is a list (batch mode)
        converted_text = data["data"]["converted_text"]
        assert isinstance(converted_text, list), "Batch mode should return list"
        assert len(converted_text) == 3
        
        # Verify each item has the expected structure
        for item in converted_text:
            assert "original" in item
            assert "translated" in item
            assert "cached" in item

    def test_semicolon_batch_response_structure(self):
        """Verify batch response contains required metadata"""
        response = client.post(
            "/translate",
            json={"message": "Hi;Hello", "language": "mr"},
        )
        data = response.json()
        assert data["data"]["batch_mode"] == True
        assert data["data"]["total_phrases"] == 2
        assert "cached_from_batch" in data["data"]

    def test_semicolon_with_empty_phrases(self):
        """Test semicolon separation with empty phrases (should be filtered)"""
        response = client.post(
            "/translate",
            json={"message": "Hello;;World", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        converted_text = data["data"]["converted_text"]
        assert len(converted_text) == 2  # Should only have 2 items (empty filtered)

    def test_semicolon_with_whitespace(self):
        """Test semicolon with whitespace around phrases"""
        response = client.post(
            "/translate",
            json={"message": " Hello ; World ; Test ", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True
        converted_text = data["data"]["converted_text"]
        # Should have 3 items, whitespace should be stripped
        assert len(converted_text) == 3

    def test_semicolon_single_phrase(self):
        """Test semicolon with only one phrase"""
        response = client.post(
            "/translate",
            json={"message": "Hello;", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True
        converted_text = data["data"]["converted_text"]
        assert len(converted_text) == 1

    def test_semicolon_batch_caching(self):
        """Test that batch translations leverage caching"""
        # First request
        response1 = client.post(
            "/translate",
            json={"message": "Test1;Test2", "language": "hi"},
        )
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request (should use cache)
        response2 = client.post(
            "/translate",
            json={"message": "Test1;Test2", "language": "hi"},
        )
        assert response2.status_code == 200
        data2 = response2.json()

        # Check that items are cached
        converted_text = data2["data"]["converted_text"]
        for item in converted_text:
            assert item["cached"] == True

    def test_semicolon_multiple_languages(self):
        """Test batch translation with different languages"""
        languages = ["hi", "mr", "gu", "bn"]
        for lang in languages:
            response = client.post(
                "/translate",
                json={"message": "Hi;Hello;Welcome", "language": lang},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == True
            assert data["data"]["batch_mode"] == True


class TestCachingBehavior:
    """Test caching functionality"""

    def test_single_message_caching(self):
        """Test that same request returns cached result"""
        message = "UniqueTestMessage123"
        
        # First request
        response1 = client.post(
            "/translate",
            json={"message": message, "language": "hi"},
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["data"]["cached"] == False

        # Second request (should be cached)
        response2 = client.post(
            "/translate",
            json={"message": message, "language": "hi"},
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Check caching
        assert data2["data"]["cached"] == True
        assert data1["data"]["converted_text"] == data2["data"]["converted_text"]

    def test_different_languages_separate_cache(self):
        """Test that different languages have separate cache entries"""
        message = "Test"
        
        # Translate to Hindi
        response1 = client.post(
            "/translate",
            json={"message": message, "language": "hi"},
        )
        data1 = response1.json()

        # Translate same message to Marathi
        response2 = client.post(
            "/translate",
            json={"message": message, "language": "mr"},
        )
        data2 = response2.json()

        # Both should be successful with different translations
        assert data1["status"] == True
        assert data2["status"] == True
        # Translations should be different
        assert data1["data"]["converted_text"] != data2["data"]["converted_text"]


class TestErrorHandling:
    """Test error handling and validation"""

    def test_empty_message(self):
        """Test translation with empty message"""
        response = client.post(
            "/translate",
            json={"message": "", "language": "hi"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == False

    def test_whitespace_only_message(self):
        """Test translation with whitespace-only message"""
        response = client.post(
            "/translate",
            json={"message": "   ", "language": "hi"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == False

    def test_invalid_language(self):
        """Test translation with invalid language code"""
        response = client.post(
            "/translate",
            json={"message": "Hello", "language": "xyz"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == False

    def test_message_too_long(self):
        """Test message that exceeds max length"""
        long_message = "x" * 10001
        response = client.post(
            "/translate",
            json={"message": long_message, "language": "hi"},
        )
        assert response.status_code == 400

    def test_missing_message_field(self):
        """Test request with missing message field"""
        response = client.post(
            "/translate",
            json={"language": "hi"},
        )
        assert response.status_code == 422

    def test_missing_language_field(self):
        """Test request with missing language field"""
        response = client.post(
            "/translate",
            json={"message": "Hello"},
        )
        assert response.status_code == 422

    def test_invalid_request_format(self):
        """Test request with invalid format"""
        response = client.post(
            "/translate",
            json={"message": 12345, "language": "hi"},  # number instead of string
        )
        assert response.status_code == 422


class TestStatsEndpoint:
    """Test statistics endpoint"""

    def test_get_stats(self):
        """Test /stats endpoint"""
        # Make at least one translation first
        client.post(
            "/translate",
            json={"message": "StatsTest", "language": "hi"},
        )

        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True
        assert data["code"] == 200
        assert "total_translations" in data["data"]
        assert "cache_stats" in data["data"]

    def test_stats_structure(self):
        """Verify stats response structure"""
        response = client.get("/stats")
        data = response.json()
        assert "status" in data
        assert "code" in data
        assert "message" in data
        assert "data" in data

    def test_stats_shows_translations(self):
        """Test that stats reflects translation count"""
        # Make a translation
        client.post(
            "/translate",
            json={"message": "CountTest", "language": "hi"},
        )

        response = client.get("/stats")
        data = response.json()
        assert data["data"]["total_translations"] >= 1


class TestCacheManagement:
    """Test cache management endpoints"""

    def test_clear_cache(self):
        """Test /cache/clear endpoint"""
        # Make a translation to populate cache
        client.post(
            "/translate",
            json={"message": "CacheTest", "language": "hi"},
        )

        # Clear cache
        response = client.post("/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True
        assert "cleared" in data["message"].lower()

    def test_clear_cache_response_structure(self):
        """Verify cache clear response structure"""
        response = client.post("/cache/clear")
        data = response.json()
        assert "status" in data
        assert "code" in data
        assert "message" in data


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_very_short_message(self):
        """Test translation of very short message"""
        response = client.post(
            "/translate",
            json={"message": "a", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True

    def test_message_with_multiple_spaces(self):
        """Test message with multiple spaces"""
        response = client.post(
            "/translate",
            json={"message": "Hello    World", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True

    def test_message_with_newlines(self):
        """Test message with newlines"""
        response = client.post(
            "/translate",
            json={"message": "Hello\nWorld", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True

    def test_message_with_tabs(self):
        """Test message with tab characters"""
        response = client.post(
            "/translate",
            json={"message": "Hello\tWorld", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True

    def test_unicode_message(self):
        """Test translation of unicode message"""
        response = client.post(
            "/translate",
            json={"message": "你好世界", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True

    def test_mixed_language_message(self):
        """Test translation of mixed language message"""
        response = client.post(
            "/translate",
            json={"message": "Hello नमस्ते", "language": "mr"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == True

    def test_only_semicolons(self):
        """Test message with only semicolons"""
        response = client.post(
            "/translate",
            json={"message": ";;;", "language": "hi"},
        )
        # Should fail because no valid phrases
        assert response.status_code == 400

    def test_semicolon_at_start(self):
        """Test message starting with semicolon"""
        response = client.post(
            "/translate",
            json={"message": ";Hello;World", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        # Should have 2 items (empty first one is filtered)
        assert len(data["data"]["converted_text"]) == 2

    def test_semicolon_at_end(self):
        """Test message ending with semicolon"""
        response = client.post(
            "/translate",
            json={"message": "Hello;World;", "language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["converted_text"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

