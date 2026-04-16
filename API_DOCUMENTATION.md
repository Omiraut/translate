# Translation API - Complete API Documentation

## Overview

The Translation API is a production-ready REST service that translates text to multiple languages using free, open-source libraries.

---

## Base URL

```
http://localhost:8000
```

### API Versioning

All endpoints are currently v1 (implicit). Future versions will use:
```
/api/v1/translate
```

---

## Authentication

Currently, the API does not require authentication (public).

For production use, consider adding:
- API Keys
- OAuth2
- JWT Tokens

---

## Rate Limiting

**Default Limit:** 60 requests per minute per IP address

**Response when limit exceeded:**
```json
{
  "status": false,
  "code": 429,
  "message": "Rate limit exceeded. Max 60 requests per 1 minute(s)",
  "data": null
}
```

---

## Response Format

All responses follow a consistent format:

```json
{
  "status": true,
  "code": 200,
  "message": "Success message",
  "data": {
    // Endpoint-specific data
  }
}
```

### Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK - Request succeeded | Translation successful |
| 400 | Bad Request - Invalid input | Empty message, unsupported language |
| 404 | Not Found | Invalid endpoint |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Translation service failed |

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check if API is running

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "timestamp": "2024-01-20T10:30:45.123456",
  "version": "1.0.0"
}
```

---

### 2. List Supported Languages

**Endpoint:** `GET /languages`

**Description:** Get all supported language codes and names

**Request:**
```bash
curl http://localhost:8000/languages
```

**Response (200 OK):**
```json
{
  "status": true,
  "code": 200,
  "data": {
    "hi": "Hindi",
    "mr": "Marathi",
    "gu": "Gujarati",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean"
  }
}
```

---

### 3. Translate Text ⭐ (Main Endpoint)

**Endpoint:** `POST /translate`

**Description:** Translate text to a target language

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "string (required)",
  "language": "string (required)"
}
```

**Parameters:**

| Field | Type | Required | Length | Description |
|-------|------|----------|--------|-------------|
| message | string | Yes | 1-10000 chars | Text to translate |
| language | string | Yes | 2 chars | Language code (e.g., 'hi', 'mr') |

**Examples:**

#### Example 1: Translate to Hindi
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi",
    "language": "hi"
  }'
```

**Response (200 OK - Fresh Translation):**
```json
{
  "status": true,
  "code": 200,
  "message": "Translation successful",
  "data": {
    "converted_text": "नमस्ते",
    "language": "hi",
    "cached": false,
    "library": "deep-translator"
  }
}
```

#### Example 2: Same Request (Cached)
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi",
    "language": "hi"
  }'
```

**Response (200 OK - From Cache):**
```json
{
  "status": true,
  "code": 200,
  "message": "Translation successful",
  "data": {
    "converted_text": "नमस्ते",
    "language": "hi",
    "cached": true
  }
}
```

#### Example 3: Invalid Language
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi",
    "language": "xyz"
  }'
```

**Response (400 Bad Request):**
```json
{
  "status": false,
  "code": 400,
  "message": "Unsupported language code 'xyz'. Supported: hi, mr, gu, bn, ta, te, kn, ml, en, es, fr, de, it, pt, ru, zh, ja, ko",
  "data": null
}
```

#### Example 4: Empty Message
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "",
    "language": "hi"
  }'
```

**Response (400 Bad Request):**
```json
{
  "status": false,
  "code": 400,
  "message": "Message cannot be empty",
  "data": null
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| status | boolean | True if successful |
| code | integer | HTTP status code |
| message | string | Human-readable message |
| data.converted_text | string | Translated text |
| data.language | string | Target language code |
| data.cached | boolean | Whether result came from cache |
| data.library | string | Translation library used (if fresh) |

---

### 4. Get Service Statistics

**Endpoint:** `GET /stats`

**Description:** Get service statistics including cache info

**Request:**
```bash
curl http://localhost:8000/stats
```

**Response (200 OK):**
```json
{
  "status": true,
  "code": 200,
  "message": "Statistics retrieved",
  "data": {
    "total_translations": 42,
    "cache_stats": {
      "total_entries": 25,
      "entries": [
        {
          "message": "Hello",
          "language": "hi",
          "cached_at": "2024-01-20T10:25:30.123456"
        },
        {
          "message": "Good morning",
          "language": "mr",
          "cached_at": "2024-01-20T10:26:15.654321"
        }
      ]
    }
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| data.total_translations | integer | Total translations served |
| data.cache_stats.total_entries | integer | Cached translations |
| data.cache_stats.entries | array | List of cached items |

---

### 5. Clear Cache

**Endpoint:** `POST /cache/clear`

**Description:** Remove all cached translations

**Request:**
```bash
curl -X POST http://localhost:8000/cache/clear
```

**Response (200 OK):**
```json
{
  "status": true,
  "code": 200,
  "message": "Cache cleared successfully",
  "data": null
}
```

---

## Error Responses

### Validation Errors (400)

When input validation fails:

```json
{
  "status": false,
  "code": 400,
  "message": "Descriptive error message",
  "data": null
}
```

**Common Messages:**
- "Message cannot be empty"
- "Message cannot contain only whitespace"
- "Message is too long (max 10000 characters)"
- "Language code cannot be empty"
- "Unsupported language code 'xyz'. Supported: ..."

---

### Server Errors (500)

When translation service fails:

```json
{
  "status": false,
  "code": 500,
  "message": "Translation failed: [error details]",
  "data": null
}
```

---

### Rate Limit Errors (429)

When rate limit is exceeded:

```json
{
  "status": false,
  "code": 429,
  "message": "Rate limit exceeded. Max 60 requests per 1 minute(s)",
  "data": null
}
```

---

## Interactive Documentation

### Swagger UI
```
http://localhost:8000/docs
```

Provides interactive exploration of all endpoints with:
- Parameter descriptions
- Example requests
- Live testing capability

### ReDoc
```
http://localhost:8000/redoc
```

Provides clean, readable API documentation

---

## Languages Supported

The API supports 18+ languages with focus on Indian languages:

**Indian Languages:**
- Hindi (hi)
- Marathi (mr)
- Gujarati (gu)
- Bengali (bn)
- Tamil (ta)
- Telugu (te)
- Kannada (kn)
- Malayalam (ml)

**International Languages:**
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)

---

## Best Practices

### 1. Error Handling

Always check the `status` field:

```python
import requests

response = requests.post("http://localhost:8000/translate", 
    json={"message": "Hi", "language": "hi"})

if response.json()["status"]:
    translated = response.json()["data"]["converted_text"]
else:
    error = response.json()["message"]
    print(f"Error: {error}")
```

### 2. Using Cache

The API automatically caches translations. For the same message+language pair:
- First request: ~100-500ms (fresh translation)
- Cached request: ~1-5ms (from cache)

### 3. Batch Translations

For multiple translations, make multiple requests:

```bash
for lang in hi mr gu bn; do
  curl -X POST http://localhost:8000/translate \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Hello\", \"language\": \"$lang\"}"
done
```

### 4. Rate Limiting

Default: 60 requests/minute per IP. Adjust via `.env`:
```
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_MINUTES=1
```

---

## Webhook/Callback Support

Not yet implemented. For async translation, consider:
1. Making requests in a queue/background job
2. Polling the stats endpoint
3. Implementing a custom callback system

---

## Pagination & Filtering

Not yet implemented. The `/languages` endpoint returns all languages. Consider implementing pagination for future versions.

---

## SDKs & Client Libraries

### Python
```python
import requests

def translate(text, language):
    response = requests.post(
        "http://localhost:8000/translate",
        json={"message": text, "language": language}
    )
    return response.json()["data"]["converted_text"]

print(translate("Hello", "hi"))  # नमस्ते
```

### cURL
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "language": "hi"}'
```

### JavaScript/Node.js
```javascript
async function translate(text, language) {
  const response = await fetch('http://localhost:8000/translate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text, language })
  });
  return response.json();
}

translate('Hello', 'hi').then(r => console.log(r.data.converted_text));
```

---

## Versioning

### Current Version: 1.0.0

**Semantic Versioning:**
- MAJOR: Breaking API changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

Future versions will use: `GET /api/v1/translate`

---

## Support & Documentation

- **API Docs:** http://localhost:8000/docs
- **GitHub:** [Project Repository]
- **Issues:** Report bugs and feature requests
- **Email:** support@translation-api.local

---

## Terms of Use

- Free and open-source
- No API keys required
- Rate limited to prevent abuse
- For personal and commercial use
- No guarantees on translation accuracy

---

## Changelog

### Version 1.0.0 (Current)
- ✅ Translation endpoint
- ✅ Caching with TTL
- ✅ Rate limiting
- ✅ Input validation
- ✅ Error handling
- ✅ Logging
- ✅ Multi-language support
- ✅ Health check
- ✅ Statistics endpoint
- ✅ Swagger documentation

### Planned (v1.1.0)
- [ ] Batch translation endpoint
- [ ] Translation history
- [ ] Custom language support
- [ ] WebSocket for real-time translation
- [ ] Advanced caching strategies

---

*Last Updated: January 2024*
